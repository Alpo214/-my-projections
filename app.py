import streamlit as st
import pandas as pd
import statsapi  # pip install MLB-StatsAPI
from datetime import date, timedelta

st.title("MLB Pitcher Strikeouts Over/Under Probability Analyzer")

def get_player_id(name):
    """Find MLBAM player ID from pitcher name."""
    results = statsapi.lookup_player(name)
    return results[0]['id'] if results else None

def get_recent_strikeouts(player_id, num_games):
    """Get most recent games with strikeout stats for this pitcher."""
    today = date.today()
    start = today - timedelta(days=180)
    schedule = statsapi.schedule(
        start_date=start.strftime('%m/%d/%Y'),
        end_date=today.strftime('%m/%d/%Y'),
        player_id=player_id
    )
    # Compile list of games with strikeout stats
    pitch_logs = []
    for game in reversed(schedule):  # Reverse for most recent games first
        for stat in game.get('pitching', []):
            if stat.get('player_id') == player_id and 'strikeOuts' in stat:
                pitch_logs.append({
                    'date': game['game_date'],
                    'opponent': game['opponent_name'],
                    'strikeouts': stat['strikeOuts']
                })
    return pitch_logs[-num_games:] if len(pitch_logs) >= num_games else pitch_logs  # last N games

pitcher_name = st.text_input("Enter Pitcher's Name (e.g., Spencer Strider):")
num_games = st.slider("How many most recent games to analyze?", min_value=3, max_value=30, value=10)
custom_line = st.number_input("Input your Over/Under Prize
