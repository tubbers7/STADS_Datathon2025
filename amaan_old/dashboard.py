import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import time

# Lade die GeoJSON-Datei (sollte im selben Verzeichnis liegen)
gdf = gpd.read_file("2_hoch.geo.json")

# Erstelle ein Dictionary, das die Bundeslandnamen ihren Geometrien zuordnet
bundesland_geoms = {row["name"]: row["geometry"] for idx, row in gdf.iterrows()}


def generate_random_points_in_bundesland(bundesland: str, num_points: int = 1000) -> pd.DataFrame:
    """
    Generiert zufällige Punkte (latitude/longitude), die innerhalb der Polygon-Grenzen
    des gewählten Bundeslandes liegen.
    """
    polygon = bundesland_geoms[bundesland]
    minx, miny, maxx, maxy = polygon.bounds

    points = []
    while len(points) < num_points:
        random_x = np.random.uniform(minx, maxx, num_points)
        random_y = np.random.uniform(miny, maxy, num_points)
        for x, y in zip(random_x, random_y):
            point = Point(x, y)
            if polygon.contains(point):
                # Beachte: x entspricht der Longitude, y der Latitude
                points.append([y, x])
            if len(points) >= num_points:
                break

    points = np.array(points)[:num_points]
    return pd.DataFrame({
        "latitude": points[:, 0],
        "longitude": points[:, 1]
    })


def main():
    st.title("Animierte Map: Punkte wechseln im Bundesland")

    # Auswahl des Bundeslandes
    bundesland = st.selectbox("Wähle ein Bundesland", list(bundesland_geoms.keys()))
    num_points = 1000
    df = generate_random_points_in_bundesland(bundesland, num_points)

    # Erstelle einen Platzhalter für die Map
    placeholder = st.empty()
    placeholder.map(df)

    # Simuliere die Animation: In jeder Iteration werden zufällig Punkte entfernt und ersetzt
    animation_iterations = 100  # z. B. 100 Schritte der Animation
    for i in range(animation_iterations):
        # Entferne zufällig 5% der Punkte
        remove_count = int(0.05 * len(df))
        if remove_count > 0:
            remove_indices = np.random.choice(df.index, size=remove_count, replace=False)
            df = df.drop(remove_indices).reset_index(drop=True)

        # Füge neue Punkte hinzu, damit die Gesamtzahl wieder num_points beträgt
        new_points = generate_random_points_in_bundesland(bundesland, num_points - len(df))
        df = pd.concat([df, new_points], ignore_index=True)

        # Aktualisiere die Map im Platzhalter
        placeholder.map(df)
        time.sleep(0.1)  # Pause zwischen den Schritten (500 ms)


if __name__ == "__main__":
    main()
