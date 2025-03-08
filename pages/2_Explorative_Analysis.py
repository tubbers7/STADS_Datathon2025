import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px

# --- Load Data ---
df = pd.read_csv("C:\\Users\\Arved\\Desktop\\STADS_Datathon2025\\final_merged_no_dupe.csv", sep=",")
# drop first column
df = df.drop(df.columns[0], axis=1)

# --- Filter Data ---
df_gender = df[(df["gender"] == 'm') | (df["gender"] == 'f')]
df_rg = df[df['risk_groups'].notnull()]


# --- Streamlit UI ---
st.title("Explorative Analysis")

st.subheader("Data Overview")
st.write(df.head())

# Plot the graph
# Add input widgets for customization
st.subheader("Extrapolated Data by Categories")

st.write("Plot 1 - Gender and Insurance Type")
st.bar_chart(df_gender, x="gender", y="extrapolated", color="insurancetype", stack=False,
             y_label = "Gender", x_label = "Extrapolated Amount of Vaccinations", horizontal=True)

st.write("Plot 2 - Age Group and Insurance Type")
st.bar_chart(df, x="age_group", y="extrapolated", color="insurancetype", stack=False,
                y_label = "Age Group", x_label = "Extrapolated Amount of Vaccinations", horizontal=True)

st.write("Plot 3 - Risk Groups and Age Group")
st.bar_chart(df_rg, x="risk_groups", y="extrapolated", color="age_group", stack=False,
                y_label = "Risk Groups", x_label = "Extrapolated Amount of Vaccinations", horizontal=True)

st.write("Plot 4 - Federal State and Age Group")
st.bar_chart(df, x="kvregion", y="extrapolated", color="age_group", stack=False,
                y_label = "Federal State", x_label = "Extrapolated Amount of Vaccinations", horizontal=True)
