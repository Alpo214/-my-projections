import streamlit as st
import pandas as pd
import statsapi
from datetime import date, timedelta

st.title("MLB Pitcher Strikeouts Over/Under Probability Analyzer")

def get_player_id(name):
    """Find MLBAM player ID from pitcher name."""
    results = statsapi.lookup_player(name)
    return results[0]['id'] if results else None

def get_recent_strikeouts(player_id, num_games):
    today = date.today()
    start = today - timedelta(days=180)
    # Get all MLB games in the last 180 days
    schedule = statsapi.schedule(
        start_date=start.strftime('%m/%d/%Y'),
        end_date=today.strftime('%m/%d/%Y'),
        sportId=1  # MLB
    )
    pitch_logs = []
    # Go through schedule in reverse (newest games last)
    for game in reversed(schedule):
        if game.get('status') != 'Final':
            continue
        box = statsapi.boxscore_data(game['game_id'])
        for team_key in ['home', 'away']:
            pitchers = box[team_key]['pitchers']
            players = box[team_key]['players']
            for pid in pitchers:
                if int(pid) == int(player_id):
                    so = players[pid]['stats']['pitching'].get('strikeOuts')
                    if so is not None:
                        pitch_logs.append({
                            'date': game['game_date'],
                            'opponent': box['away']['team'] if team_key == 'home' else box['home']['team'],
                            'strikeouts': int(so)
                        })
    pitch_logs = sorted(pitch_logs, key=lambda x: x['date'])
    return pitch_logs[-num_games:] if len(pitch_logs) >= num_games else pitch_logs

pitcher_name = st.text_input("Enter Pitcher's Name (e.g., Spencer Strider):")
num_games = st.slider("How many most recent games
