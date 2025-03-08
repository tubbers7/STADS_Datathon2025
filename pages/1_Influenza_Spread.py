import streamlit as st
import geopandas as gpd
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px
import altair as alt
st.set_page_config(page_title="CGM Demo", page_icon="✨")
# --- Load Data ---
@st.cache_data  # Caches data to improve performance
def load_data():
    df_cases = load_influenza_df()
    df_grouped = load_age_df()
    df_vac = load_vaccine_df()
    df_merged = merge_vac_cases(df_vac, df_cases)
    df_merged = df_merged.fillna(0)
    df = create_geo_df(df_merged)
    return df

df = load_data()

# --- Function to get datetime from calendar week ---
def get_datetime_from_week(year, week):
    return datetime.fromisocalendar(year, week, 1)

# --- Create list of weeks for selection ---
start_date = get_datetime_from_week(df['Year'].min(), df[df['Year'] == df['Year'].min()]['CalendarWeek'].min())
end_date = get_datetime_from_week(df['Year'].max(), df[df['Year'] == df['Year'].max()]['CalendarWeek'].max())

weeks = [start_date + timedelta(weeks=i) for i in range((end_date - start_date).days // 7 + 1)]
week_options = {week.strftime('%Y-%m-%d'): week for week in weeks}

# --- Streamlit UI ---
st.title("Influenza Cases")

selected_week_label = st.select_slider("Select Week:", options=list(week_options.keys()))
selected_date = week_options[selected_week_label]

# --- Extract year and week number ---
selected_year = selected_date.year
selected_week = selected_date.isocalendar()[1]

# --- Filter DataFrame ---
filtered_df = df[(df['Year'] == selected_year) & (df['CalendarWeek'] == selected_week)]
if filtered_df.empty:
    st.warning(f"No data available for Week {selected_week}, {selected_year}")
else:
    # Convert DataFrame to GeoDataFrame
    gdf = gpd.GeoDataFrame(filtered_df, geometry='geometry')
    
    # Ensure geometry is in GeoJSON format
    gdf = gdf.set_geometry("geometry")
    gdf = gdf.to_crs(epsg=4326)  # Convert to WGS84 if not already
    geojson_data = gdf.__geo_interface__  # Convert to GeoJSON format
    
    # Calculate dynamic center for a better view
    lat_center = gdf.geometry.centroid.y.mean()
    lon_center = gdf.geometry.centroid.x.mean()
    
    # Create Plotly Choropleth Map
    fig = px.choropleth_mapbox(
        gdf, 
        geojson=geojson_data, 
        locations=gdf.index, 
        color="InfluenzaCasesPerCapita",
        hover_name="Region",
        color_continuous_scale="YlOrRd",
        mapbox_style="carto-positron",
        center={"lat": lat_center, "lon": lon_center},
        zoom=4,#zoom_level,
        title=f"Influenza Cases Per Capita - Week {selected_week}, {selected_year}"
    )
    
    # Display in Streamlit
    st.plotly_chart(fig)

