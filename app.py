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
custom_line = st.number_input("Input your Over/Under PrizePicks line (e.g., 6.5):", step=0.5, value=6.5)

if pitcher_name:
    player_id = get_player_id(pitcher_name)
    if player_id:
        logs = get_recent_strikeouts(player_id, num_games)
        if logs:
            df = pd.DataFrame(logs)
            df['strikeouts'] = pd.to_numeric(df['strikeouts'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna(subset=['strikeouts'])

            st.write(f"Last {len(df)} games for **{pitcher_name}**")
            st.dataframe(df.sort_values('date')[['date', 'opponent', 'strikeouts']])

            # Probability calculations
            strikes = df['strikeouts']
            over_count = (strikes > custom_line).sum()
            under_count = (strikes < custom_line).sum()
            push_count = (strikes == custom_line).sum()
            total = len(df)
            prob_over = 100 * over_count / total if total else 0
            prob_under = 100 * under_count / total if total else 0
            prob_push = 100 * push_count / total if total else 0

            st.subheader("Projection & Probability (PrizePicks Line)")
            st.markdown(f"""
- **Average strikeouts**: `{strikes.mean():.2f}`
- **Your O/U line**: `{custom_line}`
- **Over**: `{over_count} times ({prob_over:.1f}%)`
- **Under**: `{under_count} times ({prob_under:.1f}%)`
- **Push (exact)**: `{push_count} times ({prob_push:.1f}%)`
""")
            if abs(prob_over - prob_under) < 5:
                st.info("No strong edge detected: probabilities nearly equal.")
            elif prob_over > prob_under:
                st.success(f"Best Probability: **Over** ({prob_over:.1f}%)")
            else:
                st.success(f"Best Probability: **Under** ({prob_under:.1f}%)")

            st.line_chart(df.set_index('date')['strikeouts'])

            st.caption("Change the O/U line or number of games and the results update instantly!")
        else:
            st.warning(f"No pitching game logs with strikeouts found for '{pitcher_name}' in the last {num_games} games.")
    else:
        st.error(f"Could not find MLB pitcher named '{pitcher_name}'. Check spelling or try another player.")
else:
    st.info("Enter a pitcher’s name to begin.")
