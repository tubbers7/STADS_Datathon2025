
import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px

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
st.title("📊 Influenza Cases Per Capita - Weekly Map (Matplotlib)")

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
    # --- Create Plotly Choropleth Map ---
    fig = px.choropleth(gdf,
                        geojson=gdf.geometry.__geo_interface__,  # Using GeoDataFrame geometry for the map
                        locations=gdf.index,
                        color="InfluenzaCasesPerCapita",  # Column for color scale
                        hover_name="Region",  # Information to display on hover
                        color_continuous_scale="YlOrRd",  # Color scale (you can change this)
                        labels={"InfluenzaCasesPerCapita": "Influenza Cases Per Capita"},
                        title=f"Influenza Cases Per Capita - Week {selected_week}, {selected_year}")

    # Update map layout to remove borders and improve appearance
    fig.update_geos(fitbounds="locations", visible=False)  # Hide borders
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})  # Remove extra margins
    
    # --- Display Plot in Streamlit ---
    st.plotly_chart(fig)
    
    # --- Create Matplotlib Choropleth Map ---
    # fig, ax = plt.subplots(figsize=(6, 6))
    # gdf.plot(column="InfluenzaCasesPerCapita", 
    #          cmap="YlOrRd", 
    #          legend=True, 
    #          legend_kwds={"label": "Influenza Cases Per Capita", "orientation": "horizontal"}, 
    #          ax=ax)

    # ax.set_title(f"Influenza Cases Per Capita - Week {selected_week}, {selected_year}")
    # ax.axis("off")  # Hide axes for a clean look

    # # --- Display Plot in Streamlit ---
    # st.pyplot(fig)
