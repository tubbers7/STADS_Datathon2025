import re
import os 
import pandas as pd
import geopandas as gpd

base_path = './Influenza_data/'
def load_influenza_df():
    df_2023 = pd.read_csv(f"{base_path}survstat_2023/Data.csv", encoding="utf-16",sep = "\t",header=[1]).fillna(0).rename(columns={'Unnamed: 0':'Bundesland'})
    df_2024 = pd.read_csv(f"{base_path}survstat_2024/Data.csv", encoding="utf-16",sep = "\t",header=[1]).fillna(0).rename(columns={'Unnamed: 0':'Bundesland'})
    df_2025 = pd.read_csv(f"{base_path}survstat_2025/Data.csv", encoding="utf-16",sep = "\t",header=[1]).fillna(0).rename(columns={'Unnamed: 0':'Bundesland'})
    df_long = pd.DataFrame()
    for df, year in zip([df_2023, df_2024, df_2025], [2023, 2024, 2025]):
        df = df.melt(id_vars=["Bundesland"], 
                          var_name="CalendarWeek", 
                          value_name="InfluenzaCases")
        df["CalendarWeek"] = df["CalendarWeek"].astype(str).str.lstrip("0").astype(int)
        df["Year"] = year
        df['InfluenzaCases'] = df['InfluenzaCases'].astype(int)
        df_long = pd.concat([df_long, df])
    return df_long

def load_age_df():
    df_2023 = pd.read_csv(f"{base_path}survstat_age/Data.csv", encoding="utf-16",sep = "\t",header=[1]).fillna(0).rename(columns={'Unnamed: 0':'Bundesland'})
    # Extract numeric age from 'Bundesland' and create age bins
    def extract_age_group(code):
        match = re.search(r'A(\d+)', code)  # Extract digits after 'A'
        if match:
            age = int(match.group(1))
            return min(age // 10 * 10, 80)  # Bin into 10-year groups, capping at 80+
        return "Unknown"
    df = df_2023.copy()
    df["AgeGroup"] = df["Bundesland"].apply(extract_age_group)
    
    # Aggregate data by AgeGroup and Gender
    df_grouped = df.groupby("AgeGroup")[["männlich", "weiblich", "divers", "unbekannt"]].sum().reset_index()
    
    # Rename columns for clarity
    df_grouped.rename(columns={"männlich": "Male", "weiblich": "Female", "divers": "NonBinary", "unbekannt": "Unknown"}, inplace=True)
    
    # Sort by AgeGroup
    #df_grouped = df_grouped.sort_values(by="AgeGroup")
    
    # Define a function to map AgeGroup to new bins
    def categorize_age(age):
        if age == "Unknown":
            return "Unknown"
        age = int(age)  # Ensure it's an integer
        if age < 30:
            return "0-29"
        elif 30 <= age < 60:
            return "30-59"
        else:
            return "60-199"
    
    # Apply the function to create a new column
    df_grouped['AgeCategory'] = df_grouped['AgeGroup'].apply(categorize_age)
    
    # Group by the new age category and sum up values
    df_grouped = df_grouped.groupby('AgeCategory')[['Male', 'Female', 'NonBinary', 'Unknown']].sum().reset_index()
    return df_grouped

def load_vaccine_df():
    file_path = "./20025-03-07_cgm-datathon-challenge-flu_riskgroupsv1.csv"
    file_path_1 = "./20025-03-07_cgm-datathon-challenge-flu_v1.csv"
    
    df = pd.read_csv(file_path, sep=";")
    df1 = pd.read_csv(file_path_1, sep=";")
    df[['Year', 'CalendarWeek']] = df['week'].str.split('-', expand=True)
    df['Year'] = df['Year'].astype(int)  # Convert to integer
    df['CalendarWeek'] = df['CalendarWeek'].astype(int)
    # Remove the gender column (you are grouping by other columns)
    df = df.drop(columns=['gender'])
    df = df.drop(columns=['age_group'])
    df = df.drop(columns=['region'])
    df = df.drop(columns=['week'])
    
    # Group by the relevant columns (week, region, age group, etc.)
    df_aggregated = df.groupby(['kvregion', 'specialization', 'Year', 'CalendarWeek'], as_index=False).agg({
        'absolute': 'sum',          # Aggregate absolute cases (sum)
        'extrapolated': 'sum'      # Aggregate extrapolated cases (sum)
    })
    return df_aggregated

def add_population_data(df):
    '''
    adds population data and per capita information
    '''
    population_counts = {'Baden-Württemberg': 11230740,
                     'Bayern': 13176426,
                     'Berlin': 3662381,
                    'Brandenburg': 2554464,
                    'Bremen': 702655,
                    'Hamburg': 1851596,
                     'Hessen': 6267546,
                    'Mecklenburg-Vorpommern' : 1578041,
                    'Niedersachsen': 8008135,
                    'Nordrhein-Westfalen': 18017520,
                     'Rheinland-Pfalz': 4125163,
                    'Saarland' : 1014047,
                    'Sachsen' : 4054689,
                    'Sachsen-Anhalt': 2144570,
                     'Schleswig-Holstein' : 2953202,
                    'Thüringen':2114870,
    }
    df['Population'] = df['Region'].map(population_counts)

    # Step 2: Scale InfluenzaCases by the population (per capita)
    df['InfluenzaCasesPerCapita'] = df['InfluenzaCases'] / df['Population']
    
    df['VaccinationsPerCapita'] = df['extrapolated'] / df['Population']
    #print(df_merged['VaccinationsPerCapita'].sum()/16)
    return df


def merge_vac_cases(df_vac, df_cases):
    # Step 1: Merge the 'kvregion' and 'Bundesland' columns into a new column called 'Region'
    df_vac['Region'] = df_vac['kvregion']
    df_cases['Region'] = df_cases['Bundesland']
    
    # Step 2: Drop the old 'kvregion' and 'Bundesland' columns
    df_vac = df_vac.drop(columns=['kvregion'])
    df_cases = df_cases.drop(columns=['Bundesland'])
    
    
    # Merge the two dataframes on 'Bundesland', 'CalendarWeek', and 'Year'
    merged_df = pd.merge(df_vac, df_cases, left_on=['Region', 'CalendarWeek', 'Year'], right_on=['Region', 'CalendarWeek', 'Year'], how='outer')
    merged_df = add_population_data(merged_df)
    return merged_df


def create_geo_df(df):
    germany_map = gpd.read_file("./vg2500/VG2500_LAN.shp")
    germany_map = germany_map.set_geometry("geometry") 
    germany_map = germany_map.loc[:15, :]
    germany_map['Region'] = germany_map['GEN']
    df = pd.merge(df, germany_map, on=['Region'], how='left')
    df = gpd.GeoDataFrame(df, geometry='geometry')
    return df

    

