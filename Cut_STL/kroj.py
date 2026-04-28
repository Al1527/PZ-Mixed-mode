import trimesh
import numpy as np
import os

def save_part(part, i, is_top, output_dir="output"):
        suffix = "_z" if is_top else ""
        part.export(os.path.join(output_dir, f"part_{i}{suffix}.stl"))
    
def split_mesh(mesh, plane_origin, plane_normal):

    slice_result = mesh.slice_plane(
        plane_origin=plane_origin,
        plane_normal=plane_normal,
        cap=True  
    )

    return slice_result


def split_into_grid(mesh, step_x=None, step_y=None, step_z=None, output_dir="output"):

    os.makedirs(output_dir, exist_ok=True)

    bounds = mesh.bounds
    min_corner, max_corner = bounds

    parts = [mesh]

    if step_x:
        new_parts = []
        x_vals = np.arange(min_corner[0] + step_x, max_corner[0], step_x)

        for part in parts:
            temp = [part]
            for x in x_vals:
                next_temp = []
                for p in temp:
                    left = p.slice_plane([x,0,0], [-1,0,0], cap=True)
                    right = p.slice_plane([x,0,0], [1,0,0], cap=True)

                    if left is not None and len(left.faces) > 0:
                        next_temp.append(left)
                    if right is not None and len(right.faces) > 0:
                        next_temp.append(right)

                temp = next_temp

            new_parts.extend(temp)

        parts = new_parts

    if step_y:
        new_parts = []
        y_vals = np.arange(min_corner[1] + step_y, max_corner[1], step_y)

        for part in parts:
            temp = [part]
            for y in y_vals:
                next_temp = []
                for p in temp:
                    a = p.slice_plane([0,y,0], [0,-1,0], cap=True)
                    b = p.slice_plane([0,y,0], [0,1,0], cap=True)

                    if a is not None and len(a.faces) > 0:
                        next_temp.append(a)
                    if b is not None and len(b.faces) > 0:
                        next_temp.append(b)

                temp = next_temp

            new_parts.extend(temp)

        parts = new_parts

    if step_z:
        new_parts = []
        z_vals = np.arange(min_corner[2] + step_z, max_corner[2], step_z)

        for part in parts:
            temp = [part]
            for z in z_vals:
                next_temp = []
                for p in temp:
                    a = p.slice_plane([0,0,z], [0,0,-1], cap=True)
                    b = p.slice_plane([0,0,z], [0,0,1], cap=True)

                    if a is not None and len(a.faces) > 0:
                        next_temp.append(a)
                    if b is not None and len(b.faces) > 0:
                        next_temp.append(b)

                temp = next_temp

            new_parts.extend(temp)

        parts = new_parts

    for i, part in enumerate(parts):
        z_center = part.bounds.mean(axis=0)[2]
        is_top = z_center > min_corner[2] + step_z
        save_part(part, i, is_top, output_dir)

    print(f"{len(parts)}")


mesh = trimesh.load("terrain_d.stl")
folder = r'C:\Users\Al05\Desktop\UMK\ZP\output'
os.makedirs(folder, exist_ok=True)

for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
            os.remove(file_path)
split_into_grid(
    mesh,
    step_x=int(input("x: ")),  
    step_y=int(input("y: ")),
    step_z=int(input("z: "))
)
