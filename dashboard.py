import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# Lade die GeoJSON-Datei (sollte im selben Verzeichnis liegen)
gdf = gpd.read_file("2_hoch.geo.json")

# Erstelle ein Dictionary, das die Bundeslandnamen ihren Geometrien zuordnet
# Wir nehmen an, dass in den Eigenschaften der Datei "name" den Bundeslandnamen enthält
bundesland_geoms = {row["name"]: row["geometry"] for idx, row in gdf.iterrows()}

def generate_random_points_in_bundesland(bundesland: str, num_points: int = 1000) -> pd.DataFrame:
    """
    Generiere zufällige Punkte (lat/lon), die innerhalb der echten Polygongrenzen
    des ausgewählten Bundeslandes liegen.
    """
    # Hole das Polygon (oder MultiPolygon) des Bundeslandes
    polygon = bundesland_geoms[bundesland]
    # Ermittle die Bounding Box des Polygons (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = polygon.bounds

    points = []
    # Wiederhole, bis wir genug Punkte haben
    while len(points) < num_points:
        # Erzeuge Stapelweise zufällige Punkte innerhalb der Bounding Box
        random_x = np.random.uniform(minx, maxx, num_points)
        random_y = np.random.uniform(miny, maxy, num_points)
        for x, y in zip(random_x, random_y):
            point = Point(x, y)
            # Prüfe, ob der Punkt im Polygon liegt
            if polygon.contains(point):
                # Beachte: Bei GeoDaten entspricht x der Longitude und y der Latitude
                points.append([y, x])
            if len(points) >= num_points:
                break

    points = np.array(points)[:num_points]
    sizes = np.random.randn(num_points) * 100  # Zufällige Größen (anpassbar)
    colors = np.random.rand(num_points, 4).tolist()  # Zufällige Farben

    return pd.DataFrame({
        "latitude": points[:, 0],
        "longitude": points[:, 1],
        "size": sizes,
        "color": colors
    })

def main():
    st.title("Map Example: German Bundesländer (exakte Grenzen)")

    # Wähle ein Bundesland aus den in der GeoJSON-Datei enthaltenen Namen
    bundesland = st.selectbox("Choose a Bundesland", list(bundesland_geoms.keys()))

    # Generiere zufällige Punkte, die innerhalb des echten Bundesland-Polygons liegen
    df = generate_random_points_in_bundesland(bundesland, num_points=1000)

    # Zeige die Punkte in der Map an
    st.map(df, latitude="latitude", longitude="longitude", size="size", color="color")

if __name__ == "__main__":
    main()
