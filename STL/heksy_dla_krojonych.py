import trimesh
import trimesh.boolean
import trimesh.repair
import numpy as np
from shapely.geometry import Polygon
import trimesh.creation
import os
import re

def generate_hex_centers(bbox_min, bbox_max, hex_size=1.0):
    """Generuje centra heksagonów - spacing wyliczony geometrycznie"""
    dx = hex_size * np.sqrt(3)      # poziomy odstęp między centrami
    dy = hex_size * 1.5             # pionowy odstęp między centrami
    
    centers = []
    row = 0
    y = bbox_min[1]
    while y <= bbox_max[1] + dy:
        x = bbox_min[0]
        offset = (row % 2) * dx / 2
        while x <= bbox_max[0] + dx:
            centers.append((x + offset, y))
            x += dx
        y += dy
        row += 1
    return centers
def create_hex_prism(cx, cy, z, hex_size, height):
    """Tworzy pojedynczy graniastosłup heksagonalny"""
    angles = np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 6
    verts_2d = [(cx + hex_size * np.cos(a), cy + hex_size * np.sin(a)) for a in angles]
    poly = Polygon(verts_2d)
    
    mesh = trimesh.creation.extrude_polygon(poly, height=height)
    mesh.apply_translation([0, 0, z])
    return mesh

def generate_hex_centers(bbox_min, bbox_max, hex_size=1.0, origin=(0.0, 0.0)):
    dx = hex_size * np.sqrt(3)
    dy = hex_size * 1.5
    
    centers = []
    row = 0
    y = origin[1]
    
    while y + dy <= bbox_min[1]:
        y += dy
        row += 1
    y -= dy
    row -= 1
    
    while y <= bbox_max[1] + dy:
        x = origin[0]
        offset = (row % 2) * dx / 2
        while x + dx <= bbox_min[0]:
            x += dx
        x -= dx
        while x <= bbox_max[0] + dx:
            centers.append((x + offset, y))
            x += dx
        y += dy
        row += 1
    
    return centers


def project_hex_onto_mesh(source_mesh, hex_size=2.0, gap=0.1, global_origin=(0.0, 0.0)):
    bbox_min = source_mesh.bounds[0]
    bbox_max = source_mesh.bounds[1]
    
    centers = generate_hex_centers(bbox_min, bbox_max, hex_size, origin=global_origin)
    
    ray_origins = np.array([
        [cx, cy, bbox_max[2] + 1.0]
        for cx, cy in centers
    ])
    ray_directions = np.tile([0, 0, -1], (len(centers), 1))
    
    intersector = trimesh.ray.ray_triangle.RayMeshIntersector(source_mesh)
    locations, ray_indices, _ = intersector.intersects_location(
        ray_origins, ray_directions, multiple_hits=False
    )
    
    hit_map = {}
    for loc, ray_idx in zip(locations, ray_indices):
        hit_map[ray_idx] = loc[2]

    centers_arr = np.array(centers)
    hit_indices = list(hit_map.keys())
    hit_xy = centers_arr[hit_indices]
    hit_z  = np.array([hit_map[i] for i in hit_indices])

    from scipy.spatial import cKDTree
    tree = cKDTree(hit_xy)

    neighbor_radius = hex_size * 2.2
    z_smoothed = hit_z.copy()
    for idx in range(len(hit_indices)):
        neighbor_idxs = tree.query_ball_point(hit_xy[idx], r=neighbor_radius)
        neighbor_z = hit_z[neighbor_idxs]
        z_smoothed[idx] = max(hit_z[idx], np.max(neighbor_z) * 0.85)

    z_base_global = bbox_min[2]
    hex_meshes = []

    for out_idx, i in enumerate(hit_indices):
        cx, cy = centers[i]
        z_top = z_smoothed[out_idx]
        try:
            h = create_hex_prism_to_base(cx, cy, z_top, hex_size - gap, z_base_global)
            hex_meshes.append(h)
        except Exception:
            continue

    if not hex_meshes:
        return None

    print(f"Łączenie {len(hex_meshes)} heksów przez boolean union...")
    result = hex_meshes[0]
    batch_size = 10
    for i in range(1, len(hex_meshes), batch_size):
        batch = hex_meshes[i:i+batch_size]
        try:
            result = trimesh.boolean.union([result] + batch, engine='manifold')
        except Exception:
            result = trimesh.util.concatenate([result] + batch)

    print("Watertight:", result.is_watertight)
    return result

def create_hex_prism_to_base(cx, cy, z_top, hex_size, z_base):
    """Hex rozciągnięty od z_base do z_top – bez dziur"""
    angles = np.linspace(0, 2 * np.pi, 7)[:-1] + np.pi / 6
    verts_2d = [(cx + hex_size * np.cos(a), cy + hex_size * np.sin(a)) for a in angles]
    poly = Polygon(verts_2d)
    
    height = z_top - z_base + 0.5  # +0.5 zapas żeby wystawały ponad powierzchnię
    if height <= 0:
        height = 0.5
    
    mesh = trimesh.creation.extrude_polygon(poly, height=height)
    mesh.apply_translation([0, 0, z_base])  # startuj od dołu
    return mesh

# ── GLOBALNY BBOX Z ORYGINALNEGO PLIKU ────────────────────────────────────────
original_stl_path = "terrain_d.stl" #sciezka do pliku oryginalnego
original_mesh = trimesh.load(original_stl_path)
global_bbox_min = original_mesh.bounds[0]
global_bbox_max = original_mesh.bounds[1]
print(f"Globalny bbox: {global_bbox_min} → {global_bbox_max}")

# ── GŁÓWNA PĘTLA ──────────────────────────────────────────────────────────────

folder_path = __path__ #sciezka do katalogu z pokrojonymi stl
output_suffix = "_hex"
hex_user = float(input("enter hex size: "))

def transform_filename(filename):
    """Dodawanie '_z' dla plików pokrojonych na górze."""
    base, ext = os.path.splitext(filename)
    match = re.search(r'part_(\d+)_z', base)
    if match:
        number = match.group(1)
        new_base = f"part_{number}_hex_z"
        return new_base + ext
    return base + output_suffix + ext

stl_files = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith(".stl") and output_suffix not in f
]

print(f"Znaleziono {len(stl_files)} plików.\n")
for filename in stl_files:
    full_path = os.path.join(folder_path, filename)
    print(f"Przetwarzam: {filename}")
    try:
        source = trimesh.load(full_path)
        print(f"  Wczytano: {len(source.faces)} faces, watertight: {source.is_watertight}")

        result = project_hex_onto_mesh(
            source,
            hex_size=hex_user,
            gap=0.0,
            global_origin=(global_bbox_min[0], global_bbox_min[1])  # wspólny punkt startowy
        )

        if result is not None:
            base, ext = os.path.splitext(filename)
            out_path = os.path.join(folder_path, transform_filename(filename))
            result.export(out_path)
            print(f"  Zapisano: {base + output_suffix + ext}\n")
        else:
            print(f"  Pominięto — brak wynikowych hexów.\n")

    except Exception as e:
        import traceback
        print(f"  Błąd: {e}")
        traceback.print_exc()
        continue
