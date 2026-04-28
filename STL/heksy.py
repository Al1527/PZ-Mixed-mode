import trimesh
import trimesh.boolean
import trimesh.repair
import numpy as np
from shapely.geometry import Polygon
import trimesh.creation
import os

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

def project_hex_onto_mesh(source_mesh, hex_size=2.0, gap=0.1):
    bbox_min = source_mesh.bounds[0]
    bbox_max = source_mesh.bounds[1]
    
    centers = generate_hex_centers(bbox_min, bbox_max, hex_size)
    
    ray_origins = np.array([
        [cx, cy, bbox_max[2] + 1.0]  # startuj PONAD modelem
        for cx, cy in centers
    ])
    ray_directions = np.tile([0, 0, -1], (len(centers), 1))  # strzelaj w dół
    
    intersector = trimesh.ray.ray_triangle.RayMeshIntersector(source_mesh)
    locations, ray_indices, _ = intersector.intersects_location(
        ray_origins, ray_directions, multiple_hits=False
    )
    
    # Mapa: który ray trafił gdzie
    hit_map = {}
    for loc, ray_idx in zip(locations, ray_indices):
        hit_map[ray_idx] = loc[2]  # Z trafienia
    
    z_base_global = bbox_min[2]
    hex_meshes = []

    for i, (cx, cy) in enumerate(centers):
        if i not in hit_map:
            continue  # ray nie trafił w mesh (poza obrysem)
        z_top = hit_map[i]
        try:
            h = create_hex_prism_to_base(cx, cy, z_top, hex_size - gap, z_base_global)
            hex_meshes.append(h)
        except Exception:
            continue

    if not hex_meshes:
        return None

    print(f"Łączenie {len(hex_meshes)} heksów przez boolean union...")
    
    # Boolean union łączy wszystkie hexy w jeden watertight solid
    result = hex_meshes[0]
    batch_size = 10  # łącz po 10 na raz żeby nie zabić RAM-u
    
    for i in range(1, len(hex_meshes), batch_size):
        batch = hex_meshes[i:i+batch_size]
        batch_merged = trimesh.util.concatenate([result] + batch)
        try:
            result = trimesh.boolean.union([result] + batch, engine='manifold')
        except Exception:
            result = batch_merged  # fallback jeśli union zawiedzie
        #print(f"  Postęp: {min(i+batch_size, len(hex_meshes))}/{len(hex_meshes)}")

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
# ── GŁÓWNA PĘTLA ──────────────────────────────────────────────────────────────

folder_path = __path__
output_suffix = "_hex"

if not os.path.isdir(folder_path):
    print(f"Błąd: folder '{folder_path}' nie istnieje.")
else:
    stl_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".stl") and output_suffix not in f
    ]

    if not stl_files:
        print("Brak plików STL w folderze.")
    else:
        print(f"Znaleziono {len(stl_files)} plików.\n")
        for filename in stl_files:
            full_path = os.path.join(folder_path, filename)
            print(f"Przetwarzam: {filename}")
            try:
                source = trimesh.load(full_path)
                print(f"  Wczytano: {len(source.faces)} faces, watertight: {source.is_watertight}")

                result = project_hex_onto_mesh(source, hex_size=5.0, gap=0.0)

                if result is not None:
                    base, ext = os.path.splitext(filename)
                    out_path = os.path.join(folder_path, base + output_suffix + ext)
                    result.export(out_path)
                    print(f"  Zapisano: {base + output_suffix + ext}\n")
                else:
                    print(f"  Pominięto — brak wynikowych hexów.\n")

            except Exception as e:
                import traceback
                print(f"  Błąd: {e}")
                traceback.print_exc()
                continue
