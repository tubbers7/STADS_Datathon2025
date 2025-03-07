import streamlit as st
import pandas as pd
import numpy as np

# 1) Define bounding boxes for each Bundesland:
#    (lat_min, lat_max, lon_min, lon_max)
BUNDESLAND_BOUNDS = {
    "Baden-Württemberg": (47.5, 49.8, 7.5, 10.5),
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

def generate_random_points_in_bundesland(bundesland: str, num_points: int = 1000) -> pd.DataFrame:
    """
    Generate a DataFrame with random points (lat/lon) uniformly distributed
    within the bounding box of the selected Bundesland.
    """
    # 2) Get bounding box
    lat_min, lat_max, lon_min, lon_max = BUNDESLAND_BOUNDS[bundesland]

    # 3) Generate random latitude, longitude, size, and color
    latitudes = np.random.uniform(lat_min, lat_max, num_points)
    longitudes = np.random.uniform(lon_min, lon_max, num_points)
    sizes = np.random.randn(num_points) * 100  # You can adjust or remove as needed
    colors = np.random.rand(num_points, 4).tolist()

    # Return a DataFrame that matches the parameter names that st.map expects by default
    # or by passing them as arguments: latitude=..., longitude=..., size=..., color=...
    return pd.DataFrame({
        "latitude": latitudes,
        "longitude": longitudes,
        "size": sizes,
        "color": colors
    })

def main():
    st.title("Map Example: German Bundesländer")

    # Let the user choose a Bundesland
    bundesland = st.selectbox("Choose a Bundesland", list(BUNDESLAND_BOUNDS.keys()))

    # Generate the random data for that Bundesland
    df = generate_random_points_in_bundesland(bundesland, num_points=1000)

    # Display the map
    st.map(df, latitude="latitude", longitude="longitude", size="size", color="color")

if __name__ == "__main__":
    main()
