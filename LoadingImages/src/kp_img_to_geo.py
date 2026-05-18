import cv2
import numpy as np
import os
import json
from collections import deque
from datetime import datetime

geo = {"features": [], "type": "FeatureCollection"}
min_height = 0


def fix_polygon(p: list) -> list:
    """
    Sprawia, że lista punktów spełnia wymogi co do minimalnej ilości punktów w MultiPolygonie, oraz co do zgodności pierwszego i ostatniego punktu
    p - lista punktów, gdzie punkt to dwuelementowa tuple lub list, np. (1,2)
    """
    if len(p) == 1:
        return [p[0]] * 4
    elif len(p) == 2:
        return [p[0], p[1], p[1], p[0]]
    else:
        p.append(p[0])
        return p


def img_to_multipolygon(img: np.array, elevation: float, scaling_multiplier=1.0) -> dict:
    """
    Generuje dict odpowiadający MultiPolygonowi dla określonego obrazka zawierającego kształt danej warstwy
    img - numpy array stanowiący obrazek z kształtem danej warstwy
    elevation - liczba oznaczająca wysokość danej warstwy
    scaling_multiplier - liczba oznaczająca wartość, przez którą należy przemnożyć koordynaty każdego punktu. Domyślnie wynosi 1.0
    """
    m = {"geometry": {"coordinates": [], "type": "MultiPolygon"}, "properties": {"elevation": elevation}, "type": "Feature"}
    cont, hier = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
    hier = hier[0]
    coords = {}
    for h in range(len(hier)):
        c = (cont[h].reshape(-1, 2) * scaling_multiplier).tolist()
        if hier[h][3] == -1:
            if h not in coords:
                coords[h] = {"outer": None, "inner": []}
            coords[h]["outer"] = fix_polygon(c)
        else:
            if hier[h][3] not in coords:
                coords[hier[h][3]] = {"outer": None, "inner": []}
            coords[hier[h][3]]["inner"].append(fix_polygon(c))
    for _ in coords:
        c = coords[_]
        m["geometry"]["coordinates"].append([])
        m["geometry"]["coordinates"][-1].append(c["outer"])
        for i in c["inner"]:
            m["geometry"]["coordinates"][-1].append(i)

    return m


def floodfill(px: tuple, color_to_change: int, target_color: int, source_img: np.array, output_base_img=None, points=set()):
    """
    Wypełnia obszar ograniczony na obrazku
    px - dwuelementowa tuple lub list, np. (1,2), oznaczająca punkt na obrazku, od którego wypełnianie należy zacząć
    color_to_change - liczba określająca kolor, który będzie zamieniany
    target_color - liczba określająca kolor, na który będzie zamieniany
    source_img - numpy array stanowiący obrazek zawierający obszar ograniczony
    output_base_img - jeśli jest None, to funkcja zwraca oryginalny source_img z zamalowanymi pikselami
                      jeśli jest numpy array, to funkcja zwraca output_base_img z zamalowanymi pikselami
                      Przykładowo, floodfill(px=(1,1), color_to_change=0, target_color=2, source_image= np.array([[0,1,0],[1,0,1],[0,1,0]],dtype=np.uint8), output_base_img=None) da wynik odpowiadający obrazkowi:
                            0 1 0
                            1 2 1
                            0 1 0
                      natomiast jeśli output_base_img=np.zeros((3,3),dtype=np.uint8), to da wynik odpowiadający obrazkowi
                            0 0 0
                            0 2 0
                            0 0 0
    points - set zawierający punkty, które, jeśli zamalowane, zostaną usunięte z setu
    Zwraca dwuelementową tuple składającą się z obrazka z wypełnionym obszarem, oraz set points po ewentualnym usunięciu punktów

    Algorytm zaimplementowany na podstawie prezentacji aut. dr Bartosza Ziemkiewicza https://moodle.mat.umk.pl/pluginfile.php/238562/mod_resource/content/1/07.Floodfill.pdf
    """
    m = source_img * 1
    if color_to_change == target_color or m[px] != color_to_change:
        if output_base_img is not None:
            return output_base_img, points
        else:
            return m, points
    Q = deque()
    Q.append(px)
    while Q:
        x, y = Q.pop()
        w = x
        e = x
        while m[w, y] == color_to_change and w >= 0:
            w = w - 1
        while m[e, y] == color_to_change:
            e = e + 1
            for i in range(w + 1, e):
                m[i, y] = target_color
                points.discard((i, y))
                if output_base_img is not None:
                    output_base_img[i, y] = target_color
            for i in range(w + 1, e):
                if i < m.shape[0] and y + 1 < m.shape[1] and m[i, y + 1] == color_to_change:
                    Q.append((i, y + 1))
                if i < m.shape[0] and y - 1 >= 0 and m[i, y - 1] == color_to_change:
                    Q.append((i, y - 1))
            if e == m.shape[0]:
                break

    if output_base_img is not None:
        return output_base_img, points
    else:
        return m, points


def find_edge(a: np.array) -> set:
    """
    Zwraca zbiór białych punktów graniczących z innym kolorem
    a - np.array stanowiący obrazek
    """
    e = a - cv2.erode(a, np.ones((3, 3), np.uint8))
    return set(map(tuple, np.column_stack(np.where(e))))

def fill_by_points(og_img: np.array, img: np.array, c1: int, c2: int, edge_points):
    """
    Wypełnia wszystkie obszary od punktów ze zbioru
    og_img - np.array zawierający obrazek odpowiadający source_img w funkcji floodfill()
    img - np.array zawierający obrazek odpowiadający output_base_img w funkcji floodfill()
    c1 - int oznaczający kolor odpowiadający color_to_change w funkcji floodfill()
    c2 - int oznaczający kolor odpowiadający target_color w funkcji floodfill()
    edge_points - zbiór (set lub list) zawierający punkty odpowiadające kolejnym px w funkcji floodfill()
                  jeśli edge_points to set, edge_points stanowi również points w funkcji floodfill()
                  jeśli edge_points to list, points=set() w funkcji floodfill
    """
    while len(edge_points) > 0:
        e = edge_points.pop()
        if type(edge_points) == type(set()):
            img, edge_points = floodfill(e, c1, c2, og_img, img, edge_points)
        else:
            img, _ = floodfill(e,c1,c2,og_img,img)

def layer(og_img: np.array, coords: dict, heights: list, contour_height: float, scaling_multiplier=1.0, output_as_img=False):
    global min_height
    current_time = str(datetime.now()).replace(":", ".")
    (b, w) = (0, 255) if contour_height > 0 else (255, 0)
    img = np.full_like(og_img, b)
    height_index = 0
    current_height = heights[0]
    while True:
        fill_by_points(og_img, img, b, 128, find_edge(cv2.bitwise_not(img)) if contour_height > 0 else find_edge(img))
        if height_index < len(heights) and current_height == heights[height_index]:
            fill_by_points(og_img, img, b, 128, coords[current_height])
            height_index += 1
        fill_by_points(og_img, img, w, 128, find_edge(cv2.bitwise_not(img)) if contour_height > 0 else find_edge(img))
        #img[img == 128] = w
        if np.array_equal(img, np.full_like(og_img, 128)):
            break

        geo["features"].append(img_to_multipolygon(img, current_height, scaling_multiplier))

        if output_as_img:
            if not os.path.exists("temp"):
                os.makedirs("temp")
            cv2.imwrite(f"temp/{current_time}_{current_height}.png", img)

        current_height = current_height - contour_height
        min_height = min(current_height,min_height)


def get_layers(img_path: str, coords: dict, contour_height: float, scaling_multiplier=1.0, output_as_img=False):
    """
    Wywołuje funkcję layer() w różnych wariantach w zależności od contour_height
    img_path - str stanowiący ścieżkę do obrazka (inputu)
    coords - dict zawierający dane o ekstremach na mapie (odpowiada layer_coords w img_to_geo())
    contour_height - liczba oznaczająca różnicę między kolejnymi parami poziomic
    scaling_multiplier - liczba oznaczająca wartość, przez którą należy przemnożyć koordynaty każdego punktu. Domyślnie wynosi 1.0
    output_as_img - jeśli jest True, w międzyczasie generuje obrazki oznaczające kolejne warstwy
    """
    global min_height
    min_height = list(coords.keys())[0]
    og_img = cv2.imread(img_path, 0)
    if contour_height > 0:
        heights = sorted(list(coords.keys()), reverse=True)
        layer(og_img, coords, heights, contour_height, scaling_multiplier, output_as_img)
    elif contour_height < 0:
        heights = sorted(list(coords.keys()))
        layer(cv2.bitwise_not(og_img), coords, heights, contour_height, scaling_multiplier, output_as_img)
        min_height += contour_height
    geo["features"].append(img_to_multipolygon(np.full_like(og_img, 255), min_height, scaling_multiplier))


def output_geojson(geo_path: str):
    """
    Zapisuje zmienną globalną geo (stanowiącą dict zawierający dane do geojsona) do pliku
    geo_path - str stanowiący ścieżkę do zapisywanego pliku
    """
    with open(geo_path, mode="w") as f:
        f.write(json.dumps(geo, indent=1))


def normalize_height():
    """Modyfikuje zmienną globalną geo (stanowiącą dict zawierający dane do geojsona) tak, że najniższa elewacja to 0, jednocześnie odpowiednio przemieszczając resztę warstw"""
    for f in geo["features"]:
        f["properties"]["elevation"] = f["properties"]["elevation"] - min_height


def img_to_geo(img_path: str, geo_path: str, layer_coords: dict, contour_height: float, scaling_multiplier=1.0, normalize=True, output_as_img=False):
    """
    Generuje geojson na podstawie obrazka
    img_path - str stanowiący ścieżkę do obrazka (inputu)
    geo_path - str stanowiący ścieżkę do geojsona (outputu)
    layer_coords - dict zawierający dane o ekstremach na mapie
                   przykładowo, layer_coords={100 : [(10,15), (20,25)], 110 : [(30,40)]} oznacza, że są 3 ekstrema:
                   2 na wysokości 100, są nimi punkty (10,15) i (20,25), oraz 1 na wysokości 110, jest nim punkt (30,40)
    contour_height - liczba oznaczająca różnicę między kolejnymi parami poziomic
    scaling_multiplier - liczba oznaczająca wartość, przez którą należy przemnożyć koordynaty każdego punktu. Domyślnie wynosi 1.0
    normalize - jeśli jest True, wywołuje funkcję normalize_height(), modyfikującą wysokości w geojsonie tak, że najniższa z nich to 0
    output_as_img - jeśli jest True, w międzyczasie generuje obrazki oznaczające kolejne warstwy
    """
    global geo
    geo = {"features": [], "type": "FeatureCollection"}
    get_layers(img_path, layer_coords, contour_height, scaling_multiplier, output_as_img)
    if normalize:
        normalize_height()
    output_geojson(geo_path)
