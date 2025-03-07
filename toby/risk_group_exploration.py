import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.express as px

# --- Load Data ---
@st.cache_data  # Caches data to improve performance

def load_data():
    df1 = pd.read_csv('/Users/toby/STADS_Datathon2025/disease_prevelance_simple.csv', sep=',')
    print(df1.columns)
    # Load the second CSV file (using semicolon as the separator)
    df2 = pd.read_csv('/Users/toby/STADS_Datathon2025/20025-03-07_cgm-datathon-challenge-flu_riskgroupsv1.csv', sep=';')
    print(df2.columns)
    # Merge the two DataFrames on 'Disease' from df2 and 'risk_groups' from df1 using an outer join
    merged_df = pd.merge(df1, df2, left_on='Disease', right_on='risk_groups', how='outer')

    merged_df = merged_df.drop(columns=['Unnamed: 0'])
    return merged_df

# Test the function by calling it and printing the head of the merged DataFrame
if __name__ == '__main__':
    df = load_data()
    print(df.head())

