import cv2
import numpy as np
from skimage.morphology import skeletonize
import subprocess
import os
from svgpathtools import svg2paths
import sys
import geojson as gj
import uuid
# Wolalabym dac potrace jako biblioteke, ale cos mi nie dzialalo -Karolina Piechowicz
POTRACE_PATH = r"potrace-1.16.win64/potrace.exe"

def uuid_path(file_extension,filepath=None):
    #Tworzy sciezke do pliku tymczasowego, jesli nie jest podana
    if filepath is None:
        return str(uuid.uuid4())+file_extension
    else:
        return filepath


def kp_img_to_pbm(img_path,pbm_path):
    #za te czesc jest odpowiedzialny ktos inny, wiec ta funkcja nie powinna byc uzywana w praktyce
    #poczatkowo dzialalam na samym emailu nie sprawdzajac githuba, wiec nie wiedzialam, co juz jest
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    binary = cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)
    skeleton = skeletonize(binary > 0)
    skeleton_img = cv2.bitwise_not((skeleton.astype(np.uint8)) * 255)
    cv2.imwrite(pbm_path, skeleton_img)


def prepped_img_to_pbm(img_path,pbm_path):
    #bierze juz obrobiona mape (tylko #000000 czern i #ffffff biel), odwraca kolory, i zapisuje ja jako pbm
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.bitwise_not(img)
    cv2.imwrite(pbm_path, img)


def pbm_to_svg(pbm_path,svg_path):
    subprocess.run([POTRACE_PATH, pbm_path, "-s", "-o", svg_path], check=True)


def prepped_img_to_svg(img_path, svg_path, pbm_path=None, remove_pbm=True):
    pbm_path = uuid_path(".pbm",pbm_path)
    prepped_img_to_pbm(img_path,pbm_path)
    pbm_to_svg(pbm_path,svg_path)
    if remove_pbm:
        os.remove(pbm_path)


def svg_to_point_list(svg_path, enlist_polygon=True, point_count=200,encircle_polygon=False):
    # Point count to liczba punktów w jednej sciezce
    # Ta funkcja nie zapisuje do pliku!
    paths, _ = svg2paths(svg_path)
    points = []

    for path in paths:
        points.append([])
        length = path.length()
        for i in range(point_count):
            l = min(i * length / (point_count - 1),length)
            x = path.point(path.ilength(l)).real
            y = path.point(path.ilength(l)).imag
            points[-1].append([x,y])
        if points[-1][0] != points[-1][-1] and encircle_polygon is True:
            points[-1].append(points[-1][0])
        if enlist_polygon:
            points[-1] = [points[-1]]

    return points

def rescale_points(points,enlist_polygon=True,max_point=30):
    #Przeskalowywuje liste punktow tak, ze najwiekszy z koordynatow wsrod wszystkich punktow wynosi max_point
    #W przypadku, gdy max_point to None, zwraca oryginalne punkty bez przeskalowywania
    if max_point is not None:
        vals = set()
        for i in range(len(points)):
            if enlist_polygon:
                for p in range(len(points[i][0])):
                    vals.add(points[i][0][p][0])
                    vals.add(points[i][0][p][1])
            else:
                for p in range(len(points[i])):
                    vals.add(points[i][p][0])
                    vals.add(points[i][p][1])
        multiplier = max_point / max(vals)
        for i in range(len(points)):
            if enlist_polygon:
                for p in range(len(points[i][0])):
                    points[i][0][p][0] = points[i][0][p][0] * multiplier
                    points[i][0][p][1] = points[i][0][p][1] * multiplier
            else:
                for p in range(len(points[i])):
                    points[i][p][0] = points[i][p][0] * multiplier
                    points[i][p][1] = points[i][p][1] * multiplier

    return points

def svg_to_multipolygon_geojson(svg_path,geojson_path,point_count=200,max_point=30):
    #Dane z SVG sa traktowane jako MultiPolygon. Zaden z Polygonow nie ma dziur.
    #Nie uzywac, zrobilam zanim sobie zdalam sprawe ze chcemy featurecollection z linestringami w srodku
    polygons = rescale_points(svg_to_point_list(svg_path,True,point_count,True),True,max_point)
    geo = gj.MultiPolygon(polygons)
    with open(geojson_path,mode="w") as f:
        gj.dump(geo,f,indent=1)

def svg_to_featurecollection_geojson(svg_path,geojson_path,point_count=200,max_point=30):
    points = rescale_points(svg_to_point_list(svg_path,False,point_count,False),False,max_point)
    l = []
    for i in range(len(points)):
        l.append(gj.LineString(points[i],properties={"elevation" : 0.0}))
    geo = gj.FeatureCollection(l)
    with open(geojson_path, mode="w") as f:
        gj.dump(geo, f, indent=1)

def prepped_img_to_featurecollection_geojson(img_path,geojson_path,pbm_path=None,svg_path=None,remove_pbm=True,remove_svg=False,point_count=200,max_point=30):
    pbm_path = uuid_path(".pbm",pbm_path)
    svg_path = uuid_path(".svg",svg_path)
    prepped_img_to_svg(img_path,svg_path,pbm_path,remove_pbm)
    svg_to_featurecollection_geojson(svg_path,geojson_path,point_count,max_point)

    if remove_svg:
        os.remove(svg_path)

if __name__ == "__main__":
    prepped_img_to_featurecollection_geojson("output.png","b.geojson",None,None,True,False,100,30)