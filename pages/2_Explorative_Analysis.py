import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
from tables_for_exploration import load_df_p1, load_df_p2,load_df_p3,load_df_p4
import plotly.express as px
st.set_page_config(page_title="CGM Demo", page_icon="✨")

# --- Load Data ---
df = pd.read_csv("./final_merged_no_dupe.csv", sep=",")
# drop first column
df = df.drop(df.columns[0], axis=1)

# --- Filter Data ---
#df_gender = df[(df["gender"] == 'm') | (df["gender"] == 'f')]
#df_rg = df[df['risk_groups'].notnull()]


# --- Streamlit UI ---
st.title("Explorative Analysis")

st.subheader("Data Overview")
st.write(df.head())

# Plot the graph
# Add input widgets for customization
st.subheader("Extrapolated Data by Categories")

st.write("Plot 1 - Gender and Insurance Type")
st.bar_chart(load_df_p1(df), x="gender", y="Ratio", color="insurancetype", stack=False,
             y_label = "Gender", x_label = "Extrapolated Vaccination Percentage", horizontal=True)

st.write("Plot 2 - Age Group and Insurance Type")
st.bar_chart(load_df_p2(df), x="age_group", y="Ratio", color="insurancetype", stack=False,
                y_label = "Age Group", x_label = "Extrapolated Vaccination Percentage", horizontal=True)

st.write("Plot 3 - Risk Groups and Age Group")
st.bar_chart(load_df_p3(df), x="risk_groups", y="Ratio", color="age_group", stack=False,
                y_label = "High Risk Individuals", x_label = "Extrapolated Vaccination Percentage", horizontal=True)

# st.write("Plot 4 - Federal State and Insurance Type")
# st.bar_chart(load_df_p4(df), x="kvregion", y="Ratio", color="age_group", stack=False,
#                 y_label = "Federal State", x_label = "Extrapolated Vaccination Percentage", horizontal=True)
