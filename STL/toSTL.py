import json
import numpy as np
from scipy.interpolate import griddata
from stl import mesh
from matplotlib.path import Path


class ContourToSTL:
    def __init__(self, resolution=1.0, max_size=1000.0, base_thickness=20.0):
        """
        resolution: rozmiar komórki siatki
        max_size: maksymalny wymiar modelu w mm (X, Y lub Z)
        base_thickness: grubość podstawy modelu w mm
        """
        self.resolution = resolution
        self.max_size = max_size
        self.scale = None
        self.base_thickness = base_thickness
        self.contour_points = []
        self.elevations = []
        self.polygons_with_holes = []
        self.grid_x = None
        self.grid_y = None
        self.grid_z = None
        self.vertices = None
        self.faces = None
        
    def load_geojson(self, filename):
        """Wczytaj poziomice z pliku GeoJSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
        for feature in data['features']:
            elevation = feature['properties']['elevation']
            geom = feature['geometry']
            geom_type = geom['type']
            coords = geom['coordinates']
        
            if geom_type == 'LineString':
                for coord in coords:
                    self.contour_points.append([coord[0], coord[1]])
                    self.elevations.append(elevation)

            elif geom_type == 'MultiLineString':
                for line in coords:
                    for coord in line:
                        self.contour_points.append([coord[0], coord[1]])
                        self.elevations.append(elevation)

            elif geom_type == 'Polygon':
                # coords[0] = outer ring, coords[1:] = holes
                outer = coords[0]
                holes = coords[1:] if len(coords) > 1 else []
                self._add_polygon(elevation, outer, holes)

            elif geom_type == 'MultiPolygon':
                # Każdy element to jeden polygon z opcjonalnymi dziurami
                for polygon in coords:
                    outer = polygon[0]
                    holes = polygon[1:] if len(polygon) > 1 else []
                    self._add_polygon(elevation, outer, holes)

            else:
                print(f"Nieobsługiwany typ geometrii: {geom_type}, pomijam")
            
        print(f"Wczytano {len(self.contour_points)} punktów z poziomic")
        

    def _add_polygon(self, elevation, outer_ring, hole_rings):
        """Dodaj polygon do listy punktów i zapamiętaj geometrię z dziurami."""
        # Dodaj punkty outer ringa do interpolacji
        for coord in outer_ring:
            self.contour_points.append([coord[0], coord[1]])
            self.elevations.append(elevation)

        # Zapamiętaj pełną geometrię (outer + holes) do maskowania
        outer_np = np.array([[c[0], c[1]] for c in outer_ring])
        holes_np = [np.array([[c[0], c[1]] for c in h]) for h in hole_rings]
        self.polygons_with_holes.append((elevation, outer_np, holes_np))

        if hole_rings:
            print(f"  Polygon elevation={elevation}: outer ring + {len(hole_rings)} dziur(a)")

    def _build_mask_for_holes(self, grid_x, grid_y):
        """
        Zwróć maskę boolean (True = punkt w dziurze, powinien mieć wartość z niższego polygonu).
        Iteruje od najwyższej elewacji do najniższej.
        """
        height, width = grid_x.shape
        points_flat = np.column_stack([grid_x.ravel(), grid_y.ravel()])

        # Maska dziur: True = punkt leży w dziurze jakiegoś polygonu
        hole_mask = np.zeros(len(points_flat), dtype=bool)

        for elevation, outer, holes in self.polygons_with_holes:
            if len(holes) == 0:
                continue

            for hole in holes:
                if len(hole) < 3:
                    continue
                path = Path(hole)
                in_hole = path.contains_points(points_flat)
                hole_mask |= in_hole

        return hole_mask.reshape(height, width)
    
    def create_heightmap(self, grid_size=None):
        if not self.contour_points:
            raise ValueError("Brak wczytanych poziomic!")
    
        points = np.array(self.contour_points)
        values = np.array(self.elevations)
    
        x_min, y_min = points.min(axis=0)
        x_max, y_max = points.max(axis=0)
    
        print(f"Zakres X: {x_min:.1f} - {x_max:.1f}")
        print(f"Zakres Y: {y_min:.1f} - {y_max:.1f}")
    
        if grid_size is None:
        # Ogranicz siatkę do maksymalnie 1000x1000 komórek
            MAX_CELLS = 1000
            ratio = (x_max - x_min) / (y_max - y_min)
            if ratio >= 1:
                grid_x = MAX_CELLS
                grid_y = int(MAX_CELLS / ratio)
            else:
                grid_y = MAX_CELLS
                grid_x = int(MAX_CELLS * ratio)
        else:
            grid_x, grid_y = grid_size

        x = np.linspace(x_min, x_max, grid_x)
        y = np.linspace(y_min, y_max, grid_y)
        self.grid_x, self.grid_y = np.meshgrid(x, y)
    
        print(f"Tworzenie siatki {grid_x}x{grid_y}...")
        self.grid_z = griddata(
            points, 
            values, 
            (self.grid_x, self.grid_y), 
            method='linear',
            fill_value=values.min()
        )

        hole_mask = self._build_mask_for_holes(self.grid_x, self.grid_y)
        if hole_mask.any():
            print(f"Znaleziono {hole_mask.sum()} punktów siatki w dziurach — korygowanie...")
            # Dla punktów w dziurach użyj wartości z niższego poziomu (nearest bez punktów wewnętrznych)
            # Najprostsze podejście: nie zmieniaj — griddata liniowy i tak interpoluje poprawnie
            # jeśli outer ring i inner ring mają tę samą elewację.
            # Ale wyzeruj wkład punktów wewnętrznych przez re-interpolację bez ich strefy.
            
            # Alternatywa: zamiast re-interpolacji, po prostu obniż dziury do poziomu niższego
            # Znajdź minimalną elewację polygonu otaczającego dziurę i użyj jej dla punktów w dziurze
            for elevation, outer, holes in self.polygons_with_holes:
                for hole in holes:
                    if len(hole) < 3:
                        continue
                    points_flat = np.column_stack([self.grid_x.ravel(), self.grid_y.ravel()])
                    path = Path(hole)
                    in_hole = path.contains_points(points_flat).reshape(self.grid_x.shape)
                    
                    if in_hole.any():
                        # Znajdź elewację tuż pod tym polygonem
                        # (zakładamy że polygony są zagnieżdżone od najniższego do najwyższego)
                        lower_elevation = elevation - 10  # TODO: dynamicznie z danych
                        
                        # Znajdź rzeczywistą niższą elewację z danych
                        unique_elevations = sorted(set(self.elevations))
                        idx = unique_elevations.index(elevation)
                        if idx > 0:
                            lower_elevation = unique_elevations[idx - 1]
                        
                        # Re-interpoluj tylko te punkty używając punktów z niższych warstw
                        lower_mask = np.array(self.elevations) <= lower_elevation
                        if lower_mask.sum() > 3:
                            lower_points = points[lower_mask]
                            lower_values = values[lower_mask]
                            hole_coords = np.column_stack([
                                self.grid_x[in_hole],
                                self.grid_y[in_hole]
                            ])
                            corrected = griddata(
                                lower_points,
                                lower_values,
                                hole_coords,
                                method='linear',
                                fill_value=lower_elevation
                            )
                            self.grid_z[in_hole] = corrected
                            print(f"    Poprawiono dziurę w elevation={elevation} → wartości ~{lower_elevation}")

    
        print(f"Wysokość min: {self.grid_z.min():.1f}, max: {self.grid_z.max():.1f}")
        return self.grid_x, self.grid_y, self.grid_z

    def generate_mesh(self):
        """Generuj mesh 3D z heightmap"""
        if self.grid_z is None:
            raise ValueError("Najpierw stwórz heightmap!")
    
        height, width = self.grid_z.shape
    
        points = np.array(self.contour_points)
        x_min, y_min = points.min(axis=0)
        x_max, y_max = points.max(axis=0)

        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = self.grid_z.max() - self.grid_z.min()

        largest_dim = max(x_range, y_range, z_range)

        if largest_dim > self.max_size:
            self.scale = self.max_size / largest_dim
            print(f"Model za duży, skaluję: {self.scale:.4f}")
        else:
            self.scale = 1.0
            print(f"Model mieści się w limicie, brak skalowania")

        print(f"Wymiary modelu: {x_range*self.scale:.1f} x {y_range*self.scale:.1f} x {z_range*self.scale:.1f} mm")
    

        z_min = self.grid_z.min()
        target_z = self.max_size - self.base_thickness
        z_normalized = (self.grid_z - z_min) * self.scale

        vertices = []
        faces = []
        vertex_map = {}

        for i in range(height):
            for j in range(width):
                idx = i * width + j
                x = (self.grid_x[i, j] - x_min) * self.scale  # normalizuj od 0
                y = (self.grid_y[i, j] - y_min) * self.scale
                z = z_normalized[i, j]
                vertices.append([x, y, z])
                vertex_map[(i, j)] = idx

        
        # Generuj wierzchołki dolnej powierzchni (podstawa)
        base_offset = len(vertices)
        for i in range(height):
            for j in range(width):
                x = (self.grid_x[i, j] - x_min) * self.scale
                y = (self.grid_y[i, j] - y_min) * self.scale
                vertices.append([x, y, -self.base_thickness])
        
        # Generuj trójkąty górnej powierzchni
        for i in range(height - 1):
            for j in range(width - 1):
                v1 = vertex_map[(i, j)]
                v2 = vertex_map[(i, j+1)]
                v3 = vertex_map[(i+1, j)]
                v4 = vertex_map[(i+1, j+1)]
                
                # Dwa trójkąty na kwadrat
                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])
        
        # Generuj trójkąty dolnej powierzchni (odwrócone)
        for i in range(height - 1):
            for j in range(width - 1):
                v1 = base_offset + i * width + j
                v2 = base_offset + i * width + (j+1)
                v3 = base_offset + (i+1) * width + j
                v4 = base_offset + (i+1) * width + (j+1)
                
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
        
        # Generuj ściany boczne
        # Lewa krawędź (j=0)
        for i in range(height - 1):
            v1_top = vertex_map[(i, 0)]
            v2_top = vertex_map[(i+1, 0)]
            v1_bot = base_offset + i * width
            v2_bot = base_offset + (i+1) * width
            faces.append([v1_top, v1_bot, v2_top])
            faces.append([v2_top, v1_bot, v2_bot])
        
        # Prawa krawędź (j=width-1)
        for i in range(height - 1):
            v1_top = vertex_map[(i, width-1)]
            v2_top = vertex_map[(i+1, width-1)]
            v1_bot = base_offset + i * width + (width-1)
            v2_bot = base_offset + (i+1) * width + (width-1)
            faces.append([v1_top, v2_top, v1_bot])
            faces.append([v2_top, v2_bot, v1_bot])
        
        # Przednia krawędź (i=0)
        for j in range(width - 1):
            v1_top = vertex_map[(0, j)]
            v2_top = vertex_map[(0, j+1)]
            v1_bot = base_offset + j
            v2_bot = base_offset + j + 1
            faces.append([v1_top, v2_top, v1_bot])
            faces.append([v2_top, v2_bot, v1_bot])
        
        # Tylna krawędź (i=height-1)
        for j in range(width - 1):
            v1_top = vertex_map[(height-1, j)]
            v2_top = vertex_map[(height-1, j+1)]
            v1_bot = base_offset + (height-1) * width + j
            v2_bot = base_offset + (height-1) * width + j + 1
            faces.append([v1_top, v1_bot, v2_top])
            faces.append([v2_top, v1_bot, v2_bot])
        
        self.vertices = np.array(vertices)
        self.faces = np.array(faces)
        
        print(f"Wygenerowano mesh: {len(vertices)} wierzchołków, {len(faces)} trójkątów")
    
    def export_stl(self, filename):
        """Eksportuj mesh do pliku STL"""
        if self.vertices is None or self.faces is None:
            raise ValueError("Najpierw wygeneruj mesh!")
        
        # Stwórz mesh numpy-stl
        terrain_mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))
        
        for i, face in enumerate(self.faces):
            for j in range(3):
                terrain_mesh.vectors[i][j] = self.vertices[face[j]]
        
        # Zapisz do pliku
        terrain_mesh.save(filename)
        print(f"✓ Zapisano do {filename}")
        print(f"  Rozmiar pliku: {terrain_mesh.data.nbytes / 1024:.1f} KB")

if __name__ == "__main__":
    # Utwórz konwerter
    converter = ContourToSTL(
        resolution=2.0,      # 2mm na komórkę siatki
        max_size=1000.0,        # Przesada pionowa
        base_thickness=20.0   # Podstawa 20mm
    )
    
    # Wczytaj poziomice z pliku
    converter.load_geojson('cont_multi.geojson')
    converter.create_heightmap()
    
    
    # Generuj mesh 3D
    converter.generate_mesh()
    
    # Eksportuj do STL
    converter.export_stl('terrain_multi.stl')

