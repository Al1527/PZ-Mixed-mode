import cv2
import numpy as np
import os
import sys
import json
import uuid
from collections import deque

def uuid_path(file_extension,filepath=None,temp_folder=False):
    #Tworzy sciezke do pliku tymczasowego, jesli nie jest podana
    p = str(uuid.uuid4())+file_extension if filepath is None else filepath
    if temp_folder:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        p = os.path.join("temp",p)
    return p

def str_img(s):
    print(str(s).replace(",","").replace("\n","").replace("[","").replace("]","\n").replace(" ","").replace("255"," ").replace("0","■")+"\n-------------------------------------------")

def points_print(points,x,y):
    a = [[0 for __ in range(y)] for _ in range(x)]
    for p in points:
        a[p[0]][p[1]] = 255
    str_img(a)

def floodfill(px, color_to_change,target_color,source_img, output_base_img=None, points = set()):
    #Przykladowo, dla px=(1,1), color_to_change=2, source_image=
    # 0 1 0
    # 1 0 1
    # 0 1 0
    # a output_base_img=None, outputem bedzie
    # 0 1 0
    # 1 2 1
    # 0 1 0
    # natomiast dla output_base_img=
    # 0 0 0
    # 0 0 0
    # 0 0 0
    # outputem jest
    # 0 0 0
    # 0 2 0
    # 0 0 0
    m = source_img*1
    if color_to_change == target_color or m[px] != color_to_change:
        #print(f"{px} - no floodfill - same color = {color_to_change == target_color} - wrong color {m[px] != color_to_change} (m[px]={m[px]}, color_to_change={color_to_change}, target_color={target_color})")
        if output_base_img is not None:
            return output_base_img,points
        else:
            return m,points
    Q = deque()
    Q.append(px)
    while Q:
        x, y = Q.pop()
        w = x
        e = x
        while m[w,y] == color_to_change and w >= 0:
            w = w-1
        while m[e,y] == color_to_change :
            e = e+1
            for i in range(w+1,e):
                m[i,y] = target_color
                points.discard((i,y))
                if output_base_img is not None:
                    output_base_img[i,y] = target_color
            for i in range(w+1,e):
                if i<m.shape[0] and y+1<m.shape[1] and m[i,y+1] == color_to_change:
                    Q.append((i,y+1))
                if i<m.shape[0] and y-1>=0 and m[i,y-1] == color_to_change:
                    Q.append((i,y-1))
            if e == m.shape[0]:
                break

    if output_base_img is not None:
        return output_base_img,points
    else:
        return m,points

def save_or_save_and_merge(base_outpath, path_suffix, img):
    if os.path.exists(base_outpath+path_suffix):
        i = cv2.imread(base_outpath + path_suffix, 0)
        cv2.imwrite(base_outpath + path_suffix, cv2.bitwise_not(cv2.add(img * 255, cv2.bitwise_not(i))))
    else:
        cv2.imwrite(base_outpath+path_suffix, cv2.bitwise_not(img*255))

def fill_out_extremums(extremum_heights, extremum_coords, og_img, pbm_path):
    for p in extremum_heights:
        img = og_img * 1
        for xy in extremum_coords[p]:
            p_img = floodfill(xy, 0, 1, img, None)[0]
            o_img = floodfill(xy, 1, 2, p_img, p_img * 0)[0] // 2
            base_outpath = f"{pbm_path}_{p}"
            save_or_save_and_merge(base_outpath, "_p.png", p_img)
            save_or_save_and_merge(base_outpath, "_i.png", o_img)

def find_edge(img, c1, c2, check8=False, output_set=True):
    points = []
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            i1, i2, j1, j2 = i-1, i+1, j-1, j+1

            if img[i, j] == c1:
                if i1 >= 0 and img[i1, j] == c2:
                    points.append((i, j))
                elif i2 < img.shape[0] and img[i2, j] == c2:
                    points.append((i, j))
                elif j1 >= 0 and img[i, j1] == c2:
                    points.append((i, j))
                elif j2 < img.shape[1] and img[i, j2] == c2:
                    points.append((i, j))

                if check8:
                    if i1 >= 0 and j1 >= 0 and img[i1, j1] == c2:
                        points.append((i, j))
                    elif i1 >= 0 and j2 < img.shape[1] and img[i1, j2] == c2:
                        points.append((i, j))
                    elif i2 < img.shape[0] and j1 >= 0 and img[i2, j1] == c2:
                        points.append((i, j))
                    elif i2 < img.shape[0] and j2 < img.shape[1] and img[i2, j2] == c2:
                        points.append((i, j))
    if output_set:
        return set(points)
    return points

def draw_layers(extremum_heights, contour_height, o, pbm_path):
    current_height = extremum_heights[0]
    m = np.full_like(o, 255)
    extrema_so_far = 0
    while not np.array_equal(m, np.full_like(m, 0)):
        points = find_edge(m, 255, 0, False)
        while points:
            p = points.pop()
            o, points = floodfill(p, 255, 0, o)
            m = floodfill(p, 0, 1, o, m)[0]
            m[m == 1] = 0
        if extrema_so_far < len(extremum_heights) and current_height == extremum_heights[extrema_so_far]:
            i = cv2.imread(f"{pbm_path}_{current_height}_i.png", 0)
            m = cv2.bitwise_and(m, i)
            o = cv2.bitwise_and(o, m)
            extrema_so_far += 1
        cv2.imwrite(f"{pbm_path}_{current_height}_l.png", m)
        current_height = current_height - contour_height

def prepped_img_to_png(img_path, png_path, peak_coords, valley_coords,contour_height, delete_nonlayers=True):
    # peak_coords i valley_coords to dict
    # w ktorym klucze to wysokosci ekstremow (od nich odejmowane/dodawane contour_heights)
    # wartosci to listy, w ktorych kazda wartosc to tuple z koordynatami XY danego ekstremum
    # contour_height to roznica wysokosci miedzy poziomicami
    #funkcja zaklada mape o czarnym tle i bialych konturach, gdzie kazdy kontur to krzywa zamknieta!!!
    #uwaga - punkty w peak_coords i valley_coords powinny byc w odwrotnej kolejnosci niz sie pokazuje w np. GIMPie, tj.
    """
    ___X__
    ______
    """
    # w GIMPie X to by było (4,1), tu musi byc (1,4)
    og_img = cv2.imread(img_path,0) // 255
    peak_heights = sorted(peak_coords.keys(),reverse=True)
    valley_heights = sorted(valley_coords.keys())

    fill_out_extremums(peak_heights,peak_coords,og_img, png_path)
    fill_out_extremums(valley_heights,valley_coords,og_img, png_path)

    o = cv2.bitwise_not(og_img*255)
    if len(peak_heights) > 0 and len(valley_heights) == 0:
        draw_layers(peak_heights,contour_height,o, png_path)
    elif len(peak_heights) == 0 and len(valley_heights) > 0:
        draw_layers(valley_heights,-contour_height,o,png_path)
    else:
        draw_layers(peak_heights,contour_height,o, png_path)
        #missing - correction for files with both valleys and hills

    if delete_nonlayers:
        p = os.path.split(png_path)
        contents = os.listdir(p[0])
        for c in contents:
            if c.startswith(p[1]+"_") and (c.endswith("_i.png") or c.endswith("_p.png")):
                os.remove(os.path.join(p[0],c))

def layer_png_to_contour(img_path,multiplier):
    img = cv2.imread(img_path, 0)
    img = cv2.bitwise_not(img)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
    l = []
    for c in contours:
        l.append((c.reshape(-1,2)*multiplier).tolist())
    return l

def layer_png_to_geojson(img_path,geojson_path,max_point=30,min_height=0):
    folder_path = os.path.split(img_path)
    filelist = os.listdir(folder_path[0])
    multiplier = max_point/max(cv2.imread(os.path.join(folder_path[0],filelist[0]),0).shape) if max_point != 0 else 1.0
    d = {}
    for f in filelist:
        if "_l.png" in f:
            elevation = int(f[len(folder_path[1])+1:-6])
            d[elevation] = {"f" : os.path.join(folder_path[0],f)}
            d[elevation]["c"] = layer_png_to_contour(d[elevation]["f"],multiplier)
            for c in range(len(d[elevation]["c"])):
                d[elevation]["c"][c].append(d[elevation]["c"][c][0])
    geo = {"features" : [], "type":"FeatureCollection"}
    keys = sorted(list(d.keys()))

    height_modifier = min_height - keys[0] if min_height is not None else 0
    for k in keys:
        for c in d[k]["c"]:
            geo["features"].append({"geometry" : {"coordinates" : c, "type" : "LineString"}, "properties" : {"elevation" : float(k + height_modifier)}, "type" : "Feature"})
    j = json.dumps(geo,indent=1)
    with open(geojson_path, mode="w") as f:
        f.write(j)

def prepped_img_to_geojson(peak_coords, valley_coords, contour_height, img_path, geojson_path, png_path=None, delete_nonlayers=True, delete_layers=True,max_point=30, min_height=0):
    png_path = uuid_path("", png_path, True)

    prepped_img_to_png(img_path,png_path,peak_coords,valley_coords,contour_height,delete_nonlayers)

    layer_png_to_geojson(png_path, geojson_path, max_point, min_height)

    if delete_layers:
        p = os.path.split(png_path)
        contents = os.listdir(p[0])
        for c in contents:
            if c.startswith(p[1] + "_") and c.endswith("_l.png"):
                os.remove(os.path.join(p[0], c))

if __name__ == "__main__":

    img_path = "example_map3.png"
    peak_coords = {110 : [(1222,1553)],100 : [(1270,3000)]}

    valley_coords = {}

    prepped_img_to_geojson(peak_coords, valley_coords, 10, img_path, "temp/geo.geojson", None, True, False, 30, 0)
