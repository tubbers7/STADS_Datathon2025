import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
st.set_page_config(page_title="CGM Demo", page_icon="✨")

# --- Load Data ---
@st.cache_data  # Caches data to improve performance
def load_data():
    df1 = pd.read_csv("./disease_prevelance_simple.csv", sep=',')
    print(df1.columns)
    # Load the second CSV file (using semicolon as the separator)
    df2 = pd.read_csv('./20025-03-07_cgm-datathon-challenge-flu_riskgroupsv1.csv', sep=';')
    print(df2.columns)
    # Merge the two DataFrames on 'Disease' from df2 and 'risk_groups' from df1 using an outer join
    merged_df = pd.merge(df1, df2, left_on='Disease', right_on='risk_groups', how='outer')

    merged_df = merged_df.drop(columns=['Unnamed: 0'])
    return merged_df

df = load_data()

st.title("Risk Group Analysis")
st.write(df.head())


# --- Data Aggregation ---
# Group by 'Disease' and calculate the mean for each percentage column.
agg_df = df.groupby("risk_groups").agg({
    "Prevelance": "mean",      # General population prevalence
    "extrapolated": "sum"       # Risk group proportion
}).reset_index()

print(agg_df.head())
print(agg_df["extrapolated"].sum())

# --- Plotting Setup ---
# Create the x-axis positions for each disease.
x = np.arange(len(agg_df["risk_groups"]))  # one position per disease
width = 0.35  # width of each bar

# Create the figure and axis.
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for general population prevalence.
bars1 = ax.bar(x - width/2, agg_df["Prevelance"], width, label="General Population")

# Plot bars for risk group proportions.
bars2 = ax.bar(x + width/2, (agg_df["extrapolated"]/df['extrapolated'].sum())*100, width, label="Risk Group")

# --- Customizing the Plot ---
ax.set_xlabel("Disease")
ax.set_ylabel("Percentage")
ax.set_title("Disease Proportions: Risk Group from Dataset vs. General Population")
ax.set_xticks(x)
ax.set_xticklabels(agg_df["risk_groups"], rotation=45, ha="right")
ax.legend()

# Optionally, annotate each bar with its height.
def autolabel(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(bars1)
autolabel(bars2)

plt.tight_layout()

st.subheader("Plot 1 - Population vs. Dataset Prevelance (using with_riskgroups)")
st.pyplot(fig)

# Assume df is your DataFrame with columns including "risk_groups", "insurancetype", and "absolute"

# 1. Calculate the total count for each insurance type across the dataset.
total_pkv = df.loc[df["insurancetype"] == "PKV", "absolute"].sum()
total_gkv = df.loc[df["insurancetype"] == "GKV", "absolute"].sum()

# 2. Group by 'risk_groups' and 'insurancetype' and sum the 'absolute' values.
agg_df = df.groupby(["risk_groups", "insurancetype"])["absolute"].sum().reset_index()

# 3. Normalize each group's count by the total for its insurance type.
def normalize(row):
    if row["insurancetype"] == "PKV":
        return (row["absolute"] / total_pkv) * 100  # percentage of PKV in that risk group
    elif row["insurancetype"] == "GKV":
        return (row["absolute"] / total_gkv) * 100  # percentage of GKV in that risk group
    else:
        return np.nan

agg_df["normalized"] = agg_df.apply(normalize, axis=1)

# 4. Pivot the table so each risk group becomes a row and each insurance type becomes a column.
pivot_df = agg_df.pivot(index="risk_groups", columns="insurancetype", values="normalized").fillna(0)

# 5. Plot the normalized percentages as a grouped bar chart.
x = np.arange(len(pivot_df.index))  # one position per risk group
width = 0.35  # width of the bars

fig, ax = plt.subplots(figsize=(10, 6))

# Get the normalized values for each insurance type.
gkv_vals = pivot_df.get("GKV", pd.Series(np.zeros(len(pivot_df.index)), index=pivot_df.index))
pkv_vals = pivot_df.get("PKV", pd.Series(np.zeros(len(pivot_df.index)), index=pivot_df.index))

bars_gkv = ax.bar(x - width/2, gkv_vals, width, label="GKV")
bars_pkv = ax.bar(x + width/2, pkv_vals, width, label="PKV")

ax.set_xlabel("Disease (Risk Group)")
ax.set_ylabel("Normalized Percentage")
ax.set_title("Normalized Percentage of Absolute Counts by Insurance Type per Risk Group")
ax.set_xticks(x)
ax.set_xticklabels(pivot_df.index, rotation=45, ha="right")
ax.legend()

# Optionally, annotate the bars with percentage values.
def autolabel(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # offset above the bar
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(bars_gkv)
autolabel(bars_pkv)

plt.tight_layout()

st.subheader('Plot 2 - Normalized Percentage of PKV and GKV Members in a given risk group')
st.pyplot(fig)

