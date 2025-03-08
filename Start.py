import streamlit as st

st.set_page_config(page_title="CGM Demo", page_icon="✨")

st.header("✨CGM: **C**ontrol via **G**enerative **M**odelling")
st.write('*Team 5 - Amaan Ansari, Arved Schreiber, Toby Fuchs, Paul Nitschke, Kai Reffert*')
#st.sidebar.success("Select a page above ⬆️")
#st.write("Welcome to the interactive Influenza data dashboard!")
import numpy as np
import random
import gymnasium as gym
import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from untitled import load_influenza_df, load_age_df, load_vaccine_df, merge_vac_cases, create_geo_df
import plotly.express as px
import altair as alt
import plotly.colors as pc

# TODO: change state and action space to state x risk_level x age_group -> Done
# TODO: initialize state space with data from Kai
# TODO: check how Amaan integrated the insights from exploratory into the LLM prompt
# TODO: integrate LLM based answers from Amaan

_POPULATION = {'Baden-Württemberg_below_60_has_disease': 4677829,
                                'Baden-Württemberg_below_60_healthy': 3197303,
                                'Baden-Württemberg_60_and_above_has_disease': 2004783,
                                'Baden-Württemberg_60_and_above_healthy': 1370273,
                                'Bavaria_below_60_has_disease': 5505271,
                                'Bavaria_below_60_healthy': 3762861,
                                'Bavaria_60_and_above_has_disease': 2359401,
                                'Bavaria_60_and_above_healthy': 1612655,
                                'Berlin_below_60_has_disease': 1567356,
                                'Berlin_below_60_healthy': 1071290,
                                'Berlin_60_and_above_has_disease': 671724,
                                'Berlin_60_and_above_healthy': 459124,
                                'Brandenburg_below_60_has_disease': 1052419,
                                'Brandenburg_below_60_healthy': 719330,
                                'Brandenburg_60_and_above_has_disease': 451036,
                                'Brandenburg_60_and_above_healthy': 308284,
                                'Bremen_below_60_has_disease': 282798,
                                'Bremen_below_60_healthy': 193292,
                                'Bremen_60_and_above_has_disease': 121199,
                                'Bremen_60_and_above_healthy': 82839,
                                'Hamburg_below_60_has_disease': 789670,
                                'Hamburg_below_60_healthy': 539741,
                                'Hamburg_60_and_above_has_disease': 338430,
                                'Hamburg_60_and_above_healthy': 231317,
                                'Hesse_below_60_has_disease': 2616693,
                                'Hesse_below_60_healthy': 1788514,
                                'Hesse_60_and_above_has_disease': 1121440,
                                'Hesse_60_and_above_healthy': 766506,
                                'Lower Saxony_below_60_has_disease': 3337917,
                                'Lower Saxony_below_60_healthy': 2281472,
                                'Lower Saxony_60_and_above_has_disease': 1430536,
                                'Lower Saxony_60_and_above_healthy': 977773,
                                'Mecklenburg-Western Pomerania_below_60_has_disease': 660700,
                                'Mecklenburg-Western Pomerania_below_60_healthy': 451590,
                                'Mecklenburg-Western Pomerania_60_and_above_has_disease': 283157,
                                'Mecklenburg-Western Pomerania_60_and_above_healthy': 193538,
                                'North Rhine-Westphalia_below_60_has_disease': 7453452,
                                'North Rhine-Westphalia_below_60_healthy': 5094446,
                                'North Rhine-Westphalia_60_and_above_has_disease': 3194336,
                                'North Rhine-Westphalia_60_and_above_healthy': 2183334,
                                'Rhineland-Palatinate_below_60_has_disease': 1702244,
                                'Rhineland-Palatinate_below_60_healthy': 1163487,
                                'Rhineland-Palatinate_60_and_above_has_disease': 729533,
                                'Rhineland-Palatinate_60_and_above_healthy': 498637,
                                'Saarland_below_60_has_disease': 408460,
                                'Saarland_below_60_healthy': 279183,
                                'Saarland_60_and_above_has_disease': 175054,
                                'Saarland_60_and_above_healthy': 119649,
                                'Saxony_below_60_has_disease': 1679105,
                                'Saxony_below_60_healthy': 1147671,
                                'Saxony_60_and_above_has_disease': 719616,
                                'Saxony_60_and_above_healthy': 491859,
                                'Saxony-Anhalt_below_60_has_disease': 893024,
                                'Saxony-Anhalt_below_60_healthy': 610384,
                                'Saxony-Anhalt_60_and_above_has_disease': 382724,
                                'Saxony-Anhalt_60_and_above_healthy': 261593,
                                'Schleswig-Holstein_below_60_has_disease': 1210341,
                                'Schleswig-Holstein_below_60_healthy': 827270,
                                'Schleswig-Holstein_60_and_above_has_disease': 518717,
                                'Schleswig-Holstein_60_and_above_healthy': 354544,
                                'Thuringia_below_60_has_disease': 876586,
                                'Thuringia_below_60_healthy': 599148,
                                'Thuringia_60_and_above_has_disease': 375679,
                                'Thuringia_60_and_above_healthy': 256777}

class InfluenzaInfectionEnv(gym.Env):
    """Custom Gym Environment for Influenza Spread Simulation"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(InfluenzaInfectionEnv, self).__init__()

        # Economic Parameters
        self.unit_price_promotion = 500_000
        self.loss_income_sick = 200

        # Population Data
        self.population = _POPULATION
        
        self.states = list(self.population.keys())
        self.state_space_dim = len(self.states)

        # Gym Spaces
        self.action_space = gym.spaces.MultiBinary(self.state_space_dim)  # Actions correspond to the 16 states
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(self.state_space_dim,), dtype=np.uint8)

        # Disease Parameters
        self.num_days_sick = 1.5
        self.n_step = 0
        self.max_steps = 28
        self.base_infection_rate = np.full(self.state_space_dim, 0.09)
        self.recovery_rate = 0.1
    
        self.intervention_effect = 0.01

        # Initialize SIR Model
        self.reset()

    def reset(self):
        """Resets the environment and returns the initial observation."""
        # Initialize S, I, R for each state
        self.S = {state: self.population[state] for state in self.states}
        self.I = {state: 0 for state in self.states}
        self.R = {state: 0 for state in self.states}

        for state in self.states:
            initial_infected = int(0.05 * self.S[state])
            self.I[state] = initial_infected
            self.S[state] -= initial_infected

        self.n_step = 0
        return self._get_observation()


    def step(self, action: np.ndarray):
        """
        Takes an action and updates the environment state.
        :param action: NumPy array of length 16 indicating intervention in each state.
        :return: Tuple (observation, reward, done, info)
        """
        self.n_step += 1
        done = self.n_step >= self.max_steps

        # Convert dictionaries to NumPy arrays for vectorized computation
        S_arr = np.array(list(self.S.values()))
        I_arr = np.array(list(self.I.values()))
        R_arr = np.array(list(self.R.values()))
        population_arr = np.array(list(self.population.values()))

        # Compute new infections and recoveries
        infection_rate = self.base_infection_rate - action*self.intervention_effect
        new_infections = (infection_rate * I_arr * S_arr) / population_arr
        new_infections = np.minimum(new_infections, S_arr).astype(int)
        recoveries = (self.recovery_rate * I_arr).astype(int)

        # Compute reward
        self.n_infections_prevented_per_group = action*self.intervention_effect*I_arr*S_arr/ population_arr
        self.n_infections_pervented_per_state = self.n_infections_prevented_per_group.reshape(-1, 4).sum(axis=1)
        economic_gain_state = self.n_infections_pervented_per_state * self.loss_income_sick * self.num_days_sick
        promotion_cost_state = action.reshape(-1, 4).sum(axis=1) * self.unit_price_promotion
        self.reward_state = economic_gain_state - promotion_cost_state
        reward = self.reward_state.sum()

        # Update state
        S_arr -= new_infections
        I_arr += new_infections - recoveries
        R_arr += recoveries

        # Convert back to dictionary for readability
        self.S = dict(zip(self.states, S_arr))
        self.I = dict(zip(self.states, I_arr))
        self.R = dict(zip(self.states, R_arr))

        return self._get_observation(), reward, done, {}

    def _get_observation(self) -> dict:
        """Returns the current state as an observation."""
        return {'S': self.S, 'I': self.I, 'R': self.R}

# Extract unique values for filters
states = sorted(set([key.split('_')[0] for key in _POPULATION.keys()]))
age_groups = ["below_60", "60_and_above"]
health_statuses = ["has_disease", "healthy"]

# Dropdown selections
selected_state = st.selectbox("Select State:", states)
selected_age = st.selectbox("Select Age Group:", age_groups)
selected_health = st.selectbox("Select Health Status:", health_statuses)

# Generate the key dynamically
action_group = f"{selected_state}_{selected_age}_{selected_health}"

# Simulation parameters
history = {
    "Weeks": [],
    "Susceptible": [],
    "Infected": [],
    "Recovered": [],
    "Reward": [],
    "rewards_state": [],
    "n_infections_prevented_state": []
}

# Initialize environment
infection_env = InfluenzaInfectionEnv()
infection_env.reset()
# Reset environment
observation = infection_env.reset()

num_weeks = infection_env.max_steps

for week in range(num_weeks):
    # Generate a random intervention action (either 0 or 1 for each state)
    #action = np.random.randint(0, 2, 16*2*2)
    action = np.zeros(infection_env.state_space_dim, dtype=int)
    # Find the index of the selected key in the state list
    if action_group in infection_env.states:
        index = infection_env.states.index(action_group)
        action[index] = 1  # Set action at the correct position

    # Take a step in the environment
    observation, reward, done, _ = infection_env.step(action)
    

    # Aggregate data
    total_S = sum(observation["S"].values())
    total_I = sum(observation["I"].values())
    total_R = sum(observation["R"].values())

    # Store history
    history["Weeks"].append(week)
    history["Susceptible"].append(total_S)
    history["Infected"].append(total_I)
    history["Recovered"].append(total_R)
    history["Reward"].append(reward)
    history["rewards_state"].append(infection_env.reward_state)
    history["n_infections_prevented_state"].append(infection_env.n_infections_pervented_per_state)
    if done:
        break

# Original states and their renamed counterparts
state_mapping = {
    "Baden-Württemberg": "Baden-Württemberg",
    "Bavaria": "Bayern",
    "Berlin": "Berlin",
    "Brandenburg": "Brandenburg",
    "Bremen": "Bremen",
    "Hamburg": "Hamburg",
    "Hesse": "Hessen",
    "Lower Saxony": "Niedersachsen",
    "Mecklenburg-Western Pomerania": "Mecklenburg-Vorpommern",
    "North Rhine-Westphalia": "Nordrhein-Westfalen",
    "Rhineland-Palatinate": "Rheinland-Pfalz",
    "Saarland": "Saarland",
    "Saxony": "Sachsen",
    "Saxony-Anhalt": "Sachsen-Anhalt",
    "Schleswig-Holstein": "Schleswig-Holstein",
    "Thuringia": "Thüringen"
}


selected_week_label = st.select_slider("Select Weeks:", options=range(1, infection_env.max_steps+1))
# Assuming `history["n_infections_prevented_state"]` contains the values corresponding to the states
values = history["n_infections_prevented_state"][selected_week_label]
reward_values = history["rewards_state"][selected_week_label]

value_dict_1 = {}
for state in states:
    state_name = state_mapping[state]
    value_dict_1[state_name] = list(values)[list(states).index(state)]
value_df_1 = pd.DataFrame(list(value_dict_1.items()), columns=["Region", "N. Infections prevented"])

value_dict_2 = {}
for state in states:
    state_name = state_mapping[state]
    value_dict_2[state_name] = list(reward_values)[list(states).index(state)]
value_df_2 = pd.DataFrame(list(value_dict_2.items()), columns=["Region", "Financial Incentive"])

value_df = pd.merge(value_df_1, value_df_2, on='Region', how='inner')
gdf = create_geo_df(value_df)

# Ensure geometry is in GeoJSON format
gdf = gdf.set_geometry("geometry")
gdf = gdf.to_crs(epsg=4326)  # Convert to WGS84 if not already
geojson_data = gdf.__geo_interface__  # Convert to GeoJSON format

# Calculate dynamic center for a better view
lat_center = gdf.geometry.centroid.y.mean()
lon_center = gdf.geometry.centroid.x.mean()

custom_color_scale = [
    [0, 'red'],      # Negative values in red
    [0.5, 'yellow'], # Zero values in yellow
    [1, 'green']     # Positive values in green
]

# Create two columns for side-by-side plots
col1, col2 = st.columns(2)
# First Choropleth Map (Effect)
with col1:
    color_scale_min = -150
    color_scale_max = 150
    fig1 = px.choropleth_mapbox(
        gdf, 
        geojson=geojson_data, 
        locations=gdf.index, 
        color="N. Infections prevented",
        hover_name="Region",
        color_continuous_scale="RdYlGn",
        range_color=[color_scale_min, color_scale_max],
        mapbox_style="carto-positron",
        center={"lat": lat_center, "lon": lon_center},
        zoom=4,
    )
    
    # Set the title dynamically for the first plot
    fig1.update_layout(title_text="Number Infections Prevented")
    
    # Remove the legend title
    fig1.update_coloraxes(colorbar_title=None)

    st.plotly_chart(fig1)

# Second Choropleth Map (Financial Incentive)
with col2:
    color_scale_min = -600000
    color_scale_max = 600000
    fig2 = px.choropleth_mapbox(
        gdf, 
        geojson=geojson_data, 
        locations=gdf.index, 
        color="Financial Incentive",
        hover_name="Region",
        color_continuous_scale="RdYlGn",
        range_color=[color_scale_min, color_scale_max],
        mapbox_style="carto-positron",
        center={"lat": lat_center, "lon": lon_center},
        zoom=4,
    )
    
    # Set the title dynamically for the second plot
    fig2.update_layout(title_text="Financial Incentive")
    
    # Remove the legend title
    fig2.update_coloraxes(colorbar_title=None)

    st.plotly_chart(fig2)



