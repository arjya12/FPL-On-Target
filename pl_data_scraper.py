## importing all required libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import sys, getopt
import csv


#standard(stats)
stats = ["player","nationality","position","squad","age","birth_year","games","games_starts","minutes","goals","assists","pens_made","pens_att","cards_yellow","cards_red","goals_per90","assists_per90","goals_assists_per90","goals_pens_per90","goals_assists_pens_per90","xg","npxg","xa","xg_per90","xa_per90","xg_xa_per90","npxg_per90","npxg_xa_per90"]
stats3 = ["players_used","possession","games","games_starts","minutes","goals","assists","pens_made","pens_att","cards_yellow","cards_red","goals_per90","assists_per90","goals_assists_per90","goals_pens_per90","goals_assists_pens_per90","xg","npxg","xa","xg_per90","xa_per90","xg_xa_per90","npxg_per90","npxg_xa_per90"]
#goalkeeping(keepers)
keepers = ["player","nationality","position","squad","age","birth_year","games_gk","games_starts_gk","minutes_gk","goals_against_gk","goals_against_per90_gk","shots_on_target_against","saves","save_pct","wins_gk","draws_gk","losses_gk","clean_sheets","clean_sheets_pct","pens_att_gk","pens_allowed","pens_saved","pens_missed_gk"]
keepers3 = ["players_used","games_gk","games_starts_gk","minutes_gk","goals_against_gk","goals_against_per90_gk","shots_on_target_against","saves","save_pct","wins_gk","draws_gk","losses_gk","clean_sheets","clean_sheets_pct","pens_att_gk","pens_allowed","pens_saved","pens_missed_gk"]
#advance goalkeeping(keepersadv)
keepersadv = ["player","nationality","position","squad","age","birth_year","minutes_90s","goals_against_gk","pens_allowed","free_kick_goals_against_gk","corner_kick_goals_against_gk","own_goals_against_gk","psxg_gk","psnpxg_per_shot_on_target_against","psxg_net_gk","psxg_net_per90_gk","passes_completed_launched_gk","passes_launched_gk","passes_pct_launched_gk","passes_gk","passes_throws_gk","pct_passes_launched_gk","passes_length_avg_gk","goal_kicks","pct_goal_kicks_launched","goal_kick_length_avg","crosses_gk","crosses_stopped_gk","crosses_stopped_pct_gk","def_actions_outside_pen_area_gk","def_actions_outside_pen_area_per90_gk","avg_distance_def_actions_gk"]
keepersadv2 = ["minutes_90s","goals_against_gk","pens_allowed","free_kick_goals_against_gk","corner_kick_goals_against_gk","own_goals_against_gk","psxg_gk","psnpxg_per_shot_on_target_against","psxg_net_gk","psxg_net_per90_gk","passes_completed_launched_gk","passes_launched_gk","passes_pct_launched_gk","passes_gk","passes_throws_gk","pct_passes_launched_gk","passes_length_avg_gk","goal_kicks","pct_goal_kicks_launched","goal_kick_length_avg","crosses_gk","crosses_stopped_gk","crosses_stopped_pct_gk","def_actions_outside_pen_area_gk","def_actions_outside_pen_area_per90_gk","avg_distance_def_actions_gk"]
#shooting(shooting)
shooting = ["player","nationality","position","squad","age","birth_year","minutes_90s","goals","pens_made","pens_att","shots_total","shots_on_target","shots_free_kicks","shots_on_target_pct","shots_total_per90","shots_on_target_per90","goals_per_shot","goals_per_shot_on_target","xg","npxg","npxg_per_shot","xg_net","npxg_net"]
shooting2 = ["minutes_90s","goals","pens_made","pens_att","shots_total","shots_on_target","shots_free_kicks","shots_on_target_pct","shots_total_per90","shots_on_target_per90","goals_per_shot","goals_per_shot_on_target","xg","npxg","npxg_per_shot","xg_net","npxg_net"]
shooting3 = ["goals","pens_made","pens_att","shots_total","shots_on_target","shots_free_kicks","shots_on_target_pct","shots_total_per90","shots_on_target_per90","goals_per_shot","goals_per_shot_on_target","xg","npxg","npxg_per_shot","xg_net","npxg_net"]


#Functions to get the data in a dataframe using BeautifulSoup
def get_tables(url, text):
    res = requests.get(url)
    comm = re.compile("<!--|-->") # Remove HTML comments
    soup = BeautifulSoup(comm.sub("", res.text), 'lxml') # Parse the HMTL
    all_tables = soup.findAll("tbody") # Find all table body(tbody) elements

    team_table = all_tables[0] # Get the fist table (team table)
    team_vs_table = all_tables[1] # Get the second table (team vs. table)
    player_table = all_tables[2] # Get the third table (player table)

    if text == 'for':
        return player_table, team_table
    elif text == 'vs':
        return player_table, team_vs_table
    else:
        raise ValueError(f"Invalid text parameter: {text}. Must be 'for' or 'vs'")

def get_frame(features, player_table):
    pre_df_player = dict() # An empty dictionary to store player data
    features_wanted_player = features # Assign features to features_wanted_player
    rows_player = player_table.find_all('tr') # Find all tr elements (rows) in the player table

    # Add index column starting from 1
    pre_df_player['index'] = [] # Add an 'index' key to the dictionary
    row_count = 1

    for row in rows_player:
        # Skip header rows or empty rows
        if not row.find('th', {"scope": "row"}):
            continue

        # Add the index for this row
        pre_df_player['index'].append(row_count)
        row_count += 1

        for f in features_wanted_player:
            if f == "player":
                name_cell = row.select_one('td[data-stat="player"] a, th[data-stat="player"] a')
                if name_cell:
                    text = name_cell.text.strip()
                else:
                    name_cell = row.select_one('td[data-stat="player"], th[data-stat="player"]')
                    text = name_cell.text.strip() if name_cell else "Unknown"
            elif f == "squad":
                squad_td = row.select_one('td[data-stat="team"]')
                if not squad_td:
                    squad_td = row.select_one('td[data-stat="squad"]')

                if squad_td:
                    squad_link = squad_td.find('a')
                    text = squad_link.text.strip() if squad_link else squad_td.text.strip()
                else:
                    text = "Unknown"
            elif f == "nationality":
                nat_cell = row.find("td", {"data-stat": "nationality"})
                if nat_cell:
                    text = ''.join(c for c in nat_cell.text.strip() if c.isupper())
                else:
                    text = "Unknown"
            elif f == "position":
                pos_cell = row.find("td", {"data-stat": "position"})
                if pos_cell:
                    # Replace comma with forward slash in position
                    text = pos_cell.text.strip().replace(',', '/')
                else:
                    text = "Unknown"
            elif f == "age":
                age_cell = row.find("td", {"data-stat": "age"})
                if age_cell:
                    text = age_cell.text.strip().split('-')[0]
                else:
                    text = "0"
            elif f == "birth_year":
                birth_cell = row.find("td", {"data-stat": "age"})
                if birth_cell:
                    age_text = birth_cell.text.strip()
                    age = int(age_text.split('-')[0])
                    text = str(2021 - age)
                else:
                    text = "0"
            else:
                cell = row.find("td", {"data-stat": f})
                text = cell.text.strip() if cell else "0"

            if text == '':
                text = '0'

            if f not in ['player', 'nationality', 'position', 'squad', 'age', 'birth_year']:
                try:
                    text = float(text.replace(',', ''))
                except ValueError:
                    text = 0.0
            elif f == "age":
                try:
                    text = int(float(text))
                except ValueError:
                    text = 0

            if f in pre_df_player:
                pre_df_player[f].append(text)
            else:
                pre_df_player[f] = [text]

    df_player = pd.DataFrame.from_dict(pre_df_player)
    # Set the index column as the DataFrame index and drop it from the columns
    df_player.set_index('index', inplace=True)
    df_player.index.name = None  # Remove the index name

    return df_player

def get_frame_team(features, team_table):
    pre_df_squad = dict()
    features_wanted_squad = features
    rows_squad = team_table.find_all('tr')

    for row in rows_squad:
        if row.find('th', {"scope": "row"}) is not None:
            name = row.find('th', {"data-stat": "team"}).text.strip().encode().decode("utf-8")
            if 'squad' in pre_df_squad:
                pre_df_squad['squad'].append(name)
            else:
                pre_df_squad['squad'] = [name]

            for f in features_wanted_squad:
                cell = row.find("td", {"data-stat": f})
                if cell is None:
                    text = '0'
                else:
                    text = cell.text.strip().encode().decode("utf-8")

                if text == '':
                    text = '0'

                if f not in ['player', 'nationality', 'position', 'squad', 'age', 'birth_year']:
                    text = float(text.replace(',', ''))

                if f in pre_df_squad:
                    pre_df_squad[f].append(text)
                else:
                    pre_df_squad[f] = [text]

    df_squad = pd.DataFrame.from_dict(pre_df_squad)
    return df_squad

def frame_for_category(category,top,end,features):
    url = (top + category + end)
    player_table, team_table = get_tables(url,'for')
    df_player = get_frame(features, player_table)
    return df_player

def frame_for_category_team(category, top, end, features, text):
    url = (top + category + end.replace('/stats', ''))
    player_table, team_table = get_tables(url, text)
    df_team = get_frame_team(features, team_table)
    return df_team



#Function to get the player data for outfield player, includes all categories - standard stats, shooting
#passing, passing types, goal and shot creation, defensive actions, possession, and miscallaneous
def get_outfield_data(top, end):
    df1 = frame_for_category('stats',top,end,stats)
    df2 = frame_for_category('shooting',top,end,shooting2)
    df = pd.concat([df1, df2], axis=1)
    df = df.loc[:,~df.columns.duplicated()]
    return df


def get_team_data(top, end, text):
    df1 = frame_for_category_team('stats', top, end, stats3, text)
    df4 = frame_for_category_team('shooting', top, end, shooting3, text)
    df = pd.concat([df1, df4], axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

#This cell is to get the data FOR all teams in any competition

#Go to the 'Standard stats' page of the league
#For Premier League 2020/21, the link is this: https://fbref.com/en/comps/9/stats/Premier-League-Stats
#Remove the 'stats', and pass the first and third part of the link as parameters like below
df_team = get_team_data('https://fbref.com/en/comps/9/','/Premier-League-Stats','for')

#Save csv file to Desktop
df_team.to_csv('PL2021_teams.csv',index=False)
df_team.index = df_team.index + 1
files.download('PL2021_teams.csv')

df_team

#This cell is to get the outfield player data for any competition

#Go to the 'Standard stats' page of the league
#For Premier League 2020/21, the link is this: https://fbref.com/en/comps/9/stats/Premier-League-Stats
#Remove the 'stats', and pass the first and third part of the link as parameters like below
df_outfield = get_outfield_data('https://fbref.com/en/comps/9/','/Premier-League-Stats')

#Save csv file to Desktop
df_outfield.to_csv('PL2021_Outfield.csv', index=False)
files.download('PL2021_Outfield.csv')

df_outfield