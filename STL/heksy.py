import trimesh
import numpy as np
from shapely.geometry import Polygon
import trimesh.creation

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
    
    from trimesh.proximity import closest_point
    query_points = np.array([[cx, cy, (bbox_min[2] + bbox_max[2]) / 2] for cx, cy in centers])
    closest, distances, _ = closest_point(source_mesh, query_points)
    
    z_base_global = bbox_min[2]
    hex_meshes = []

    for i, (cx, cy) in enumerate(centers):
        z_top = closest[i][2]
        try:
            h = create_hex_prism_to_base(cx, cy, z_top, hex_size - gap, z_base_global)
            hex_meshes.append(h)
        except Exception as e:
            continue

    if not hex_meshes:
        return None

    print(f"Łączenie {len(hex_meshes)} heksów przez boolean union...")
    
    # Boolean union łączy wszystkie hexy w jeden watertight solid
    import trimesh.boolean
    result = hex_meshes[0]
    batch_size = 10  # łącz po 10 na raz żeby nie zabić RAM-u
    
    for i in range(1, len(hex_meshes), batch_size):
        batch = hex_meshes[i:i+batch_size]
        batch_merged = trimesh.util.concatenate([result] + batch)
        try:
            result = trimesh.boolean.union([result] + batch, engine='manifold')
        except Exception:
            result = batch_merged  # fallback jeśli union zawiedzie
        print(f"  Postęp: {min(i+batch_size, len(hex_meshes))}/{len(hex_meshes)}")

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
# ── UŻYCIE ──────────────────────────────────────────────────────────────────

# Wczytaj swój model
source = trimesh.load("terrain1.stl")

# Generuj siatkę hex (dostosuj parametry)
hex_grid = project_hex_onto_mesh(
    source_mesh=source,
    hex_size=3.0,      # rozmiar hexa (promień)
    gap=0.0            # odstęp między heksami
)

if hex_grid is not None:
    hex_grid.export("hex_grid.stl")
    print("Zapisano: hex_grid.stl")
