import streamlit as st
import pandas as pd
import statsapi
from datetime import date, timedelta

st.title("MLB Pitcher Strikeouts Over/Under Probability Analyzer")

def get_player_id(name):
    results = statsapi.lookup_player(name)
    return results[0]['id'] if results else None

def get_recent_strikeouts(player_id, num_games):
    today = date.today()
    start = today - timedelta(days=180)
    # ONLY use sportId=1! DO NOT add player_id anywhere!
    schedule = statsapi.schedule(
        start_date=start.strftime('%m/%d/%Y'),
        end_date=today.strftime('%m/%d/%Y'),
        sportId=1          # ← This is valid
    )
    pitch_logs = []
    # Go through schedule in reverse (most recent games last)
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
num_games = st.slider("How many most recent games to analyze?", min_value=3, max_value=30, value=10)
custom_line = st.number_input("Input your Over/Under PrizePicks line (e.g., 6.5):", step=0.5, value=6.5)

if pitcher_name:
    player_id = get_player_id(pitcher_name)
    if player_id:
        logs = get_recent_strikeouts(player_id, num_games)
        if logs:
            df = pd.DataFrame(logs)
            df['strikeouts'] = pd.to_numeric(df['strikeouts'])
            df['date'] = pd.to_datetime(df['date'])
            st.write(f"Last {len(df)} games for **{pitcher_name}**")
            st.dataframe(df[['date', 'opponent', 'strikeouts']].sort_values('date'))

            over = (df['strikeouts'] > custom_line).sum()
            under = (df['strikeouts'] < custom_line).sum()
            push = (df['strikeouts'] == custom_line).sum()
            total = len(df)
            p_over = 100 * over / total if total else 0
            p_under = 100 * under / total if total else 0
            p_push = 100 * push / total if total else 0

            st.subheader("Projection & Probability (PrizePicks Line)")
            st.markdown(f"""
- **Average strikeouts**: `{df['strikeouts'].mean():.2f}`
- **Your O/U line**: `{custom_line}`
- **Over**: `{over} times ({p_over:.1f}%)`
- **Under**: `{under} times ({p_under:.1f}%)`
- **Push (exact)**: `{push} times ({p_push:.1f}%)`
""")
            if abs(p_over - p_under) < 5:
                st.info("No strong edge detected: probabilities nearly equal.")
            elif p_over > p_under:
                st.success(f"Best Probability: **Over** ({p_over:.1f}%)")
            else:
                st.success(f"Best Probability: **Under** ({p_under:.1f}%)")

            st.line_chart(df.set_index('date')['strikeouts'])
            st.caption("Change the O/U line or number of games and the results update instantly!")
        else:
            st.warning(f"No pitching game logs with strikeouts found for '{pitcher_name}' in the last {num_games} games.")
    else:
        st.error(f"Could not find MLB pitcher named '{pitcher_name}'. Check spelling or try another player.")
else:
    st.info("Enter a pitcher’s name to begin.")

