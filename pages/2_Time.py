 
import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px
import altair as alt
import seaborn as sns
st.set_page_config(page_title="CGM Demo", page_icon="✨")

# --- Load Data ---
@st.cache_data  # Caches data to improve performance
def load_data():
    file_path = "./20025-03-07_cgm-datathon-challenge-flu_riskgroupsv1.csv"
    file_path_1 = "./20025-03-07_cgm-datathon-challenge-flu_v1.csv"
    df = pd.read_csv(file_path, sep=";")
    df[['Year', 'CalendarWeek']] = df['week'].str.split('-', expand=True)
    df['Year'] = df['Year'].astype(int)  # Convert Year to integer
    df['CalendarWeek'] = df['CalendarWeek'].astype(int)  # Convert CalendarWeek to integer
    # Create 'Date' column from 'Year' and 'CalendarWeek'
    df['Date'] = df.apply(lambda row: datetime.fromisocalendar(row['Year'], row['CalendarWeek'], 1), axis=1)
    
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' column is in datetime format
    return df

df = load_data()

column_options = ['kvregion', 'region', 'specialization', 'gender', 'age_group', 'risk_groups'
                   #'insurancecode', 'insurancetype', 
                    #'absolute', 'extrapolated', 'Year', 'CalendarWeek', 'Date'
                 ]#df.columns.tolist()  # Get a list of column names from the DataFrame
selected_column = st.selectbox("Select column to differentiate:", column_options)
plot_type = st.selectbox("Select plot type:", ['extrapolated', 'absolute'])
# Group by 'Date' and the selected column, and calculate the mean of 'extrapolated'
df_grouped = df.groupby(['Date', selected_column]).agg({plot_type: 'sum'}).reset_index()

# Generate a color palette for each unique value in the selected column
colors = sns.color_palette("Set2", n_colors=df[selected_column].nunique())  # You can adjust the palette name (e.g., "Set2", "Set1", etc.)

# List of different markers to differentiate the trends
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*']  # You can add more markers if necessary

# Plotting the time series with different colors and markers for each unique value in the selected column
#plt.figure(figsize=(10, 6))
#for i, v in enumerate(df[selected_column].unique()):
#    plt.plot(df_grouped.loc[df_grouped[selected_column] == v, 'Date'], 
#             df_grouped.loc[df_grouped[selected_column] == v, plot_type], 
#             marker=markers[i % len(markers)],  # Cycle through markers if there are too many categories
#             color=colors[i], 
#             label=f'{selected_column} = {v}')  # Label each value with a color and marker
#
#plt.legend()
#plt.title(f"Extrapolated Values by {selected_column} Over Time")
#plt.xlabel('Date')
#plt.ylabel(f'{plot_type} Value')
#plt.xticks(rotation=45)
#plt.tight_layout()

# Display the plot in Streamlit
#st.pyplot(plt)

# --- Create the Plot with Seaborn ---
plt.figure(figsize=(10, 6))

# Use Seaborn lineplot for time series
sns.lineplot(data=df_grouped, 
             x='Date', 
             y=plot_type, 
             hue=selected_column,  # This will differentiate the lines by the selected column
             marker='o',  # Adds markers to the line
             palette='Set2',  # Set color palette
             dashes=False)  # Disables dashes for the lines, making them solid

# --- Plot Customization ---
plt.title(f"{plot_type.capitalize()} Values by {selected_column.capitalize()} Over Time")
plt.xlabel('Date')
plt.ylabel(f'{plot_type.capitalize()} Value')
plt.xticks(rotation=45)
plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(plt)
