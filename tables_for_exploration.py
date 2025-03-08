import pandas as pd
base_path = './'
df = pd.read_csv(f'{base_path}final_merged_no_dupe.csv')

new_df = pd.DataFrame(columns=['Federal State', 'Age Group', 'Ground Population'])
new_df.loc[len(new_df)] = ['Baden-Württemberg', '0-29', (1645+550+656+718)*1000]
new_df.loc[len(new_df)] = ['Baden-Württemberg', '30-59', (782+744+724+674+769+890)*1000]
new_df.loc[len(new_df)] = ['Baden-Württemberg', '60-199', (822+651+542+1118)*1000]

new_df.loc[len(new_df)] = ['Bayern', '0-29', (1921+627+730+830)*1000]
new_df.loc[len(new_df)] = ['Bayern', '30-59', (954+890+870+809+935+1081)*1000]
new_df.loc[len(new_df)] = ['Bayern', '60-199', (964+774+646+1331)*1000]

new_df.loc[len(new_df)] = ['Berlin', '0-29', (544+161+204+274)*1000]
new_df.loc[len(new_df)] = ['Berlin', '30-59', (347+314+277+221+227+267)*1000]
new_df.loc[len(new_df)] = ['Berlin', '60-199', (227+177+170+352)*1000]

new_df.loc[len(new_df)] = ['Brandenburg', '0-29', (352+112+105+88)*1000]
new_df.loc[len(new_df)] = ['Brandenburg', '30-59', (132+165+187+141+178+217)*1000]
new_df.loc[len(new_df)] = ['Brandenburg', '60-199', (234+188+150+300)*1000]

new_df.loc[len(new_df)] = ['Bremen', '0-29', (99+33+42+51)*1000]
new_df.loc[len(new_df)] = ['Bremen', '30-59', (49+45+43+39+44+51)*1000]
new_df.loc[len(new_df)] = ['Bremen', '60-199', (46+37+32+68)*1000]

new_df.loc[len(new_df)] = ['Hamburg', '0-29', (277+88+106+152)*1000]
new_df.loc[len(new_df)] = ['Hamburg', '30-59', (159+145+133+119+126+138)*1000]
new_df.loc[len(new_df)] = ['Hamburg', '60-199', (111+86+74+167)*1000]

new_df.loc[len(new_df)] = ['Hessen', '0-29', (925+320+339+396)*1000]
new_df.loc[len(new_df)] = ['Hessen', '30-59', (438+413+413+389+442+525)*1000]
new_df.loc[len(new_df)] = ['Hessen', '60-199', (449+370+311+637)*1000]

arved_df = pd.read_excel('state_pops.xlsx')
arved_df.head()

final_ground_age_by_state = pd.concat([arved_df, new_df]).reset_index()
print(final_ground_age_by_state['Ground Population'].sum())
final_ground_age_by_state.head(50)

#Plot 1
def load_df_p1(df):
    df_p1 = df.copy()
    df_p1 = df_p1[['gender', 'insurancetype', 'extrapolated']]
    group_cols = ['gender', 'insurancetype']
    agg_col = 'extrapolated'
    df_p1 = df_p1.groupby(group_cols).agg({agg_col: "sum"}).reset_index()
    df_p1 = df_p1[(df_p1['gender'] == 'f') | (df_p1['gender'] == 'm')]
    df_p1['Ground Population'] = [37600000, 4420000, 35400000, 4280000]
    df_p1['Ratio'] = (df_p1['extrapolated']/df_p1['Ground Population'])*100
    df_p1['Ratio'] = df_p1['Ratio'].clip(upper=100)
    return df_p1

load_df_p1(df).head()

#Plot 2 - age, insurance
def load_df_p2(df):
    df_p2 = df.copy()
    df_p2 = df_p2[['age_group', 'insurancetype', 'extrapolated']]
    group_cols = ['age_group', 'insurancetype']
    agg_col = 'extrapolated'
    df_p2 = df_p2.groupby(group_cols).agg({agg_col: "sum"}).reset_index()
    df_p2 = df_p2.sort_values(by=['insurancetype'])
    df_p2['Ground Population'] = [22290000, 29720000, 22290000, 2610000, 3480000, 2610000]
    print(df_p2['Ground Population'].sum())
    df_p2['Ratio'] = (df_p2['extrapolated']/df_p2['Ground Population'])*100
    df_p2['Ratio'] = df_p2['Ratio'].clip(upper=100)
    return df_p2

load_df_p2(df).head(25)

#Plot 3 - risk and age
def load_df_p3(df):
    df_p3 = df.copy()
    df_p3['risk_groups'] = df['risk_groups'].notna().astype(int)
    df_p3 = df_p3[['age_group', 'risk_groups', 'extrapolated']]
    group_cols = ['age_group', 'risk_groups']
    agg_col = 'extrapolated'
    df_p3 = df_p3.groupby(group_cols).agg({agg_col: "sum"}).reset_index()
    df_p3 = df_p3.sort_values(by=['risk_groups'])
    df_p3['Ground Population'] = [2500000, 10000000, 14000000, 23750000, 20000000, 8000000]
    df_p3['Ratio'] = (df_p3['extrapolated']/df_p3['Ground Population'])*100
    df_p3['Ratio'] = df_p3['Ratio'].clip(upper=100)
    return df_p3

load_df_p3(df).head(25)

#Plot 4 - Federal State and Insurance Type
def load_df_p4(df):
    df_p4 = df.copy()
    df_p4 = df_p4[['kvregion', 'age_group', 'extrapolated']]
    group_cols = ['kvregion', 'age_group']
    agg_col = 'extrapolated'
    df_p4 = df_p4.groupby(group_cols).agg({agg_col: "sum"}).reset_index()

    merged_df_p4 = pd.merge(df_p4, final_ground_age_by_state, left_on=['kvregion','age_group'], right_on=['Federal State', 'Age Group'])
    #print(merged_df_p4.head(5))
    merged_df_p4 = merged_df_p4[['kvregion', 'age_group', 'extrapolated', 'Ground Population']]
    df_p4 = merged_df_p4.copy()
    df_p4['Ratio'] = (df_p4['extrapolated']/df_p4['Ground Population'])*100
    df_p4['Ratio'] = df_p4['Ratio'].clip(upper=100)
    return df_p4
load_df_p4(df).head(60)