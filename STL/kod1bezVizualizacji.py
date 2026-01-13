import json
import numpy as np
from scipy.interpolate import griddata
from stl import mesh
import matplotlib.pyplot as plt

class ContourToSTL:
    def __init__(self, resolution=1.0, scale_z=1.0, base_thickness=5.0):
        """
        resolution: rozmiar komórki siatki (im mniejszy, tym więcej detali)
        scale_z: przesada pionowa (jak bardzo wyciągnąć wysokości)
        base_thickness: grubość podstawy modelu w mm
        """
        self.resolution = resolution
        self.scale_z = scale_z
        self.base_thickness = base_thickness
        self.contour_points = []
        self.elevations = []
        
    def load_geojson(self, filename):
        """Wczytaj poziomice z pliku GeoJSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for feature in data['features']:
            elevation = feature['properties']['elevation']
            coords = feature['geometry']['coordinates']
            
            # Dodaj każdy punkt z poziomnicy
            for coord in coords:
                x, y = coord[0], coord[1]
                self.contour_points.append([x, y])
                self.elevations.append(elevation)
        
        print(f"Wczytano {len(self.contour_points)} punktów z poziomic")
        
    def load_svg_polylines(self, filename):
        """Wczytaj poziomice z prostego formatu SVG (polyline)"""
        # TODO: Implementacja parsowania SVG
        # Można użyć biblioteki svg.path lub xml.etree.ElementTree
        pass
    
    def create_heightmap(self, grid_size=None):
        """
        Przekształć wektorowe poziomice w regularną siatkę wysokości
        grid_size: (width, height) w komórkach siatki, None = auto
        """
        if not self.contour_points:
            raise ValueError("Brak wczytanych poziomic!")
        
        points = np.array(self.contour_points)
        values = np.array(self.elevations)
        
        # Znajdź zakres danych
        x_min, y_min = points.min(axis=0)
        x_max, y_max = points.max(axis=0)
        
        print(f"Zakres X: {x_min:.1f} - {x_max:.1f}")
        print(f"Zakres Y: {y_min:.1f} - {y_max:.1f}")
        
        # Stwórz regularną siatkę
        if grid_size is None:
            grid_x = int((x_max - x_min) / self.resolution) + 1
            grid_y = int((y_max - y_min) / self.resolution) + 1
        else:
            grid_x, grid_y = grid_size
        
        x = np.linspace(x_min, x_max, grid_x)
        y = np.linspace(y_min, y_max, grid_y)
        self.grid_x, self.grid_y = np.meshgrid(x, y)
        
        # Interpolacja wysokości
        print(f"Tworzenie siatki {grid_x}x{grid_y}...")
        self.grid_z = griddata(
            points, 
            values, 
            (self.grid_x, self.grid_y), 
            method='linear',  # 'linear', 'cubic' lub 'nearest'
            fill_value=values.min()  # Wypełnij obszary poza pozionicami
        )
        
        print(f"Wysokość min: {self.grid_z.min():.1f}, max: {self.grid_z.max():.1f}")
        return self.grid_x, self.grid_y, self.grid_z
    
    """def visualize_heightmap(self):
        ""Podgląd mapy wysokości przed eksportem"" #dodac po 1 "
        if self.grid_z is None:
            raise ValueError("Najpierw stwórz heightmap!")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Mapa 2D
        im = ax1.contourf(self.grid_x, self.grid_y, self.grid_z, levels=20, cmap='terrain')
        ax1.set_title('Mapa wysokości (2D)')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        plt.colorbar(im, ax=ax1, label='Wysokość')
        
        # Mapa 3D
        ax2 = fig.add_subplot(122, projection='3d')
        ax2.plot_surface(self.grid_x, self.grid_y, self.grid_z, cmap='terrain', alpha=0.8)
        ax2.set_title('Podgląd 3D')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Wysokość')
        
        plt.tight_layout()
        plt.show()
    """
    def generate_mesh(self):
        """Generuj mesh 3D z heightmap"""
        if self.grid_z is None:
            raise ValueError("Najpierw stwórz heightmap!")
        
        height, width = self.grid_z.shape
        
        # Normalizuj wysokości do zakresu 0-scale_z
        z_min = self.grid_z.min()
        z_range = self.grid_z.max() - z_min
        z_normalized = (self.grid_z - z_min) / z_range * self.scale_z
        
        vertices = []
        faces = []
        
        # Generuj wierzchołki górnej powierzchni
        vertex_map = {}
        for i in range(height):
            for j in range(width):
                idx = i * width + j
                x = self.grid_x[i, j]
                y = self.grid_y[i, j]
                z = z_normalized[i, j]
                vertices.append([x, y, z])
                vertex_map[(i, j)] = idx
        
        # Generuj wierzchołki dolnej powierzchni (podstawa)
        base_offset = len(vertices)
        for i in range(height):
            for j in range(width):
                x = self.grid_x[i, j]
                y = self.grid_y[i, j]
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

# ========== PRZYKŁAD UŻYCIA ==========

if __name__ == "__main__":
    # Utwórz konwerter
    converter = ContourToSTL(
        resolution=2.0,      # 2mm na komórkę siatki
        scale_z=20.0,        # Przesada pionowa 20mm
        base_thickness=5.0   # Podstawa 5mm
    )
    
    # Wczytaj poziomice z pliku
    converter.load_geojson('contours.geojson')
    
    # Stwórz heightmap
    converter.create_heightmap()
    
    # Podgląd (opcjonalnie)
    #converter.visualize_heightmap()
    
    # Generuj mesh 3D
    converter.generate_mesh()
    
    # Eksportuj do STL
    converter.export_stl('terrain.stl')
    
    print("\n✓ Gotowe! Otwórz terrain.stl w slicerze lub Blenderze")
