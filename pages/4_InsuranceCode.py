import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px
st.set_page_config(page_title="CGM Demo", page_icon="✨")

# --- Load Data ---
df = pd.read_csv("./final_merged_no_dupe.csv", sep=",")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#st.set_page_config(layout="wide")

# Load data
dfr = pd.read_csv("./final_merged_no_dupe.csv", sep=",")

# Insurance code mapping
insurancecode_mapping = {
    "375": "Schutzimpfung",
    "2": "Überweisungen",
    "1": "(Impf-) Beratung",
    "377": "Zusatzinjektion bei ",
    "5": "Symptombezogene Untersuchung",
    "3": "lange Beratung",
    "7": "Organsystemuntersuchung",
    "250": "Blutentnahme",
    "89111": "Standardimpfung",
    "89112": "Indikationsimpfung",
    "89112Y": "Reiseimpfung (beruflich)",
    "89112Z": "Satzungsimpfung over 60",
    "89112T": "Satzungsimpfung under 60",
}

# Map insurance codes to their descriptions
dfr['insurancecode_text'] = dfr['insurancecode'].map(insurancecode_mapping).fillna(dfr['insurancecode'])

# Count occurrences
insurance_counts = dfr['insurancecode_text'].value_counts()

# Streamlit app
st.title("Insurance Code Distribution")

# Plot 1: All insurance codes
st.subheader("All Insurance Codes")

# Create a Matplotlib figure for all insurance codes with a log scale
fig1, ax1 = plt.subplots(figsize=(40, 6))  # Increase the figure width to 12 inches
all_counts = dfr['insurancecode'].value_counts()
ax1.bar(all_counts.index, all_counts.values)
ax1.set_yscale('log')
ax1.set_xlabel('Insurance Code')
ax1.set_ylabel('Counts (log scale)')
ax1.set_title('All Insurance Codes Distribution')

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)
st.pyplot(fig1)

# Plot 2: Top 15 insurance codes
st.subheader("Top 15 Insurance Codes")

top_15 = insurance_counts.head(15)

# Create a Matplotlib figure for the top 15 insurance codes with a log scale
fig2, ax2 = plt.subplots()
ax2.bar(top_15.index, top_15.values)
ax2.set_yscale('log')
ax2.set_xlabel('Insurance Code')
ax2.set_ylabel('Counts (log scale)')
ax2.set_title('Top 15 Insurance Codes Distribution')

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)
st.pyplot(fig2)