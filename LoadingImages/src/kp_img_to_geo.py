import cv2
import numpy as np
import os
import json
from collections import deque
from datetime import datetime

geo = {"features": [], "type": "FeatureCollection"}

#dodac spowrotem normalizacje wysokosci do 0

def fix_polygon(p):
    if len(p) == 1:
        return [p[0]] * 4
    elif len(p) == 2:
        return [p[0], p[1], p[1], p[0]]
    else:
        p.append(p[0])
        return p

def img_to_multipolygon(img, elevation, scaling_multiplier=1.0):
    m = {"geometry" : {"coordinates" : [], "type" : "MultiPolygon"}, "properties" : {"elevation" : elevation}, "type" : "Feature"}
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

def find_edge(a):
    e = a - cv2.erode(a, np.ones((3,3), np.uint8))
    return set(map(tuple,np.column_stack(np.where(e))))

def layer(og_img, coords, heights, contour_height, scaling_multiplier=1.0, output_as_img=False):
    current_time = str(datetime.now()).replace(":",".")
    (b,w) = (0,255) if contour_height > 0 else (255,0)
    img = np.full_like(og_img, b)
    height_index = 0
    current_height = heights[0]
    while True:
        edge_points = find_edge(cv2.bitwise_not(img)) if contour_height > 0 else find_edge(img)
        while len(edge_points) > 0:
            e = edge_points.pop()
            og_img, edges = floodfill(e, b, w, og_img, None, edge_points)
            img, _ = floodfill(e, w, 128, og_img, img)
        if height_index < len(heights) and current_height == heights[height_index]:
            for h in coords[current_height]:
                og_img, _ = floodfill(h, b, w, og_img, None)
                img, _ = floodfill(h, w, 128, og_img, img)
            height_index += 1
        img[img == 128] = w
        if np.array_equal(img, np.full_like(og_img, w)):
            break

        geo["features"].append(img_to_multipolygon(img, current_height, scaling_multiplier))

        if output_as_img:
            if not os.path.exists("temp"):
                os.makedirs("temp")
            cv2.imwrite(f"temp/{current_time}_{current_height}.png", img)

        current_height = current_height - contour_height



def get_layers(img_path, coords, contour_height, scaling_multiplier=1.0, output_as_img=False):
    og_img = cv2.imread(img_path,0)
    if contour_height > 0:
        heights = sorted(list(coords.keys()),reverse=True)
        layer(og_img, coords, heights, contour_height,  scaling_multiplier, output_as_img)
    elif contour_height < 0:
        heights = sorted(list(coords.keys()))
        layer(cv2.bitwise_not(og_img), coords, heights, contour_height, scaling_multiplier, output_as_img)

def output_geojson(geo_path):
    with open(geo_path,mode="w") as f:
        f.write(json.dumps(geo,indent=1))

def img_to_geo(img_path, geo_path, layer_coords, contour_height, scaling_multiplier=1.0,  output_as_img=False):
    get_layers(img_path, layer_coords, contour_height, scaling_multiplier, output_as_img)
    output_geojson(geo_path)
