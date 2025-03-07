import streamlit as st
import pandas as pd
import numpy as np
import random
from shapely.geometry import Polygon, Point

# Für alle anderen Bundesländer verwenden wir weiterhin einfache Bounding Boxes
BUNDESLAND_BOUNDS = {
    "Bayern": (47.2, 50.6, 9.0, 13.8),
    "Berlin": (52.3, 52.7, 13.0, 13.6),
    "Brandenburg": (51.3, 53.6, 11.2, 14.8),
    "Bremen": (52.99, 53.7, 8.39, 9.13),
    "Hamburg": (53.3, 53.7, 9.7, 10.3),
    "Hessen": (49.4, 51.7, 7.8, 10.2),
    "Mecklenburg-Vorpommern": (53.0, 54.7, 10.7, 14.3),
    "Niedersachsen": (51.3, 53.8, 6.5, 11.5),
    "Nordrhein-Westfalen": (50.3, 52.5, 5.9, 9.7),
    "Rheinland-Pfalz": (49.0, 50.8, 6.1, 8.5),
    "Saarland": (49.1, 49.7, 6.4, 7.3),
    "Sachsen": (50.2, 51.7, 12.0, 15.0),
    "Sachsen-Anhalt": (50.9, 53.1, 10.6, 13.1),
    "Schleswig-Holstein": (54.3, 54.9, 8.2, 10.0),
    "Thüringen": (50.2, 51.7, 9.8, 12.7),
}

def read_poly_file(file_path: str) -> Polygon:
    """
    Liest eine .poly-Datei und gibt ein Shapely-Polygon zurück.
    Das Format der Datei:
      - Die erste Zeile enthält den Namen.
      - Danach folgen Blöcke: Jede Ringdefinition beginnt (oft mit einer ID-Zeile),
        gefolgt von Zeilen mit Koordinaten (Longitude Latitude) und endet mit "END".
      - Die Datei endet mit einer zusätzlichen "END"-Zeile.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Die erste Zeile enthält den Namen (kann ignoriert werden)
    rings = []
    current_ring = []
    # Zeilen ab der zweiten Zeile einlesen
    for line in lines[1:]:
        line = line.strip()
        if line.upper() == "END":
            if current_ring:
                rings.append(current_ring)
                current_ring = []
        elif line.isdigit() or (line.startswith('-') and line[1:].isdigit()):
            # Eine mögliche Ring-ID, ignoriere sie
            continue
        else:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    # Annahme: Die Koordinate ist im Format "lon lat"
                    lon = float(parts[0])
                    lat = float(parts[1])
                    current_ring.append((lon, lat))
                except ValueError:
                    continue

    if not rings:
        st.error("Kein gültiger Polygonring in der .poly-Datei gefunden.")
        return None

    # Erster Ring = Außengrenze, weitere Ringe = Löcher (falls vorhanden)
    exterior = rings[0]
    holes = rings[1:] if len(rings) > 1 else None
    return Polygon(exterior, holes)

def generate_random_points_in_polygon(polygon: Polygon, num_points: int = 1000):
    """
    Generiert num_points Zufallspunkte, die innerhalb des gegebenen Polygons liegen.
    """
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    while len(points) < num_points:
        lon = random.uniform(minx, maxx)
        lat = random.uniform(miny, maxy)
        p = Point(lon, lat)
        if polygon.contains(p):
            points.append((lat, lon))
    return points

def generate_random_points_in_bundesland(bundesland: str, num_points: int = 1000) -> pd.DataFrame:
    if bundesland == "Baden-Württemberg":
        # Nutze die .poly-Datei, um die exakte Grenze zu laden
        polygon = read_poly_file("bw.poly")
        if polygon is None:
            return pd.DataFrame()
        points = generate_random_points_in_polygon(polygon, num_points)
        latitudes, longitudes = zip(*points)
        sizes = np.random.randn(num_points) * 100  # z.B. für Visualisierungszwecke
        colors = np.random.rand(num_points, 4).tolist()
        return pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "size": sizes,
            "color": colors
        })
    else:
        # Für andere Bundesländer die bisherigen Bounding Boxen verwenden
        lat_min, lat_max, lon_min, lon_max = BUNDESLAND_BOUNDS[bundesland]
        latitudes = np.random.uniform(lat_min, lat_max, num_points)
        longitudes = np.random.uniform(lon_min, lon_max, num_points)
        sizes = np.random.randn(num_points) * 100
        colors = np.random.rand(num_points, 4).tolist()
        return pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "size": sizes,
            "color": colors
        })

def main():
    st.title("Map Example: German Bundesländer")
    # Füge Baden-Württemberg in die Auswahl ein
    bundesland_options = list(BUNDESLAND_BOUNDS.keys()) + ["Baden-Württemberg"]
    bundesland = st.selectbox("Wähle ein Bundesland", bundesland_options)
    df = generate_random_points_in_bundesland(bundesland, num_points=1000)
    if not df.empty:
        st.map(df, latitude="latitude", longitude="longitude")

if __name__ == "__main__":
    main()
