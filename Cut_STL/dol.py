import os
import trimesh
import numpy as np

FOLDER = r"./output"

CUT_WIDTH = 10.0
CUT_DEPTH = 5.0
CUT_HEIGHT = 5.0

def create_cut_boxes(mesh):

    bounds = mesh.bounds
    min_corner, max_corner = bounds

    xmin, ymin, zmin = min_corner
    xmax, ymax, zmax = max_corner

    xcenter = (xmin + xmax) / 2
    ycenter = (ymin + ymax) / 2

    boxes = []

    box = trimesh.creation.box(
        extents=[CUT_DEPTH, CUT_WIDTH, CUT_HEIGHT]
    )

    box.apply_translation([
        xmin + CUT_DEPTH / 2,
        ycenter,
        zmin + CUT_HEIGHT / 2
    ])

    boxes.append(box)

    box = trimesh.creation.box(
        extents=[CUT_DEPTH, CUT_WIDTH, CUT_HEIGHT]
    )

    box.apply_translation([
        xmax - CUT_DEPTH / 2,
        ycenter,
        zmin + CUT_HEIGHT / 2
    ])

    boxes.append(box)
    box = trimesh.creation.box(
        extents=[CUT_WIDTH, CUT_DEPTH, CUT_HEIGHT]
    )

    box.apply_translation([
        xcenter,
        ymin + CUT_DEPTH / 2,
        zmin + CUT_HEIGHT / 2
    ])

    boxes.append(box)

    box = trimesh.creation.box(
        extents=[CUT_WIDTH, CUT_DEPTH, CUT_HEIGHT]
    )

    box.apply_translation([
        xcenter,
        ymax - CUT_DEPTH / 2,
        zmin + CUT_HEIGHT / 2
    ])

    boxes.append(box)

    return boxes

def repair_mesh(mesh):

    mesh.remove_unreferenced_vertices()

    try:
        mesh.remove_duplicate_faces()
    except:
        pass

    try:
        mesh.remove_degenerate_faces()
    except:
        pass

    mesh.fix_normals()
    parts = mesh.split(only_watertight=False)
    fixed_parts = []

    for p in parts:

        try:

            p.fix_normals()

            if p.volume < 0:
                p.invert()

            if p.is_watertight:
                fixed_parts.append(p)

        except:
            pass


    repaired = trimesh.util.concatenate(fixed_parts)
    repaired.remove_unreferenced_vertices()
    repaired.fix_normals()

    return repaired

def process_stl(filepath):

    try:

        mesh = trimesh.load_mesh(filepath)
        mesh = repair_mesh(mesh)
        cut_boxes = create_cut_boxes(mesh)
        combined_cut = trimesh.util.concatenate(cut_boxes)
        result = mesh.difference(combined_cut)
        result.remove_unreferenced_vertices()
        result.fix_normals()
        result.export(filepath)

    except Exception as e:

        print(e)

def process_folder(folder):

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".stl") and "_z" not in f
    ]

    for file in files:
        fullpath = os.path.join(folder, file)
        process_stl(fullpath)

if __name__ == "__main__":

    process_folder(FOLDER)
