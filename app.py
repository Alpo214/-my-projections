import streamlit as st
import pandas as pd
import statsapi  # Python wrapper for public MLB Stats API

st.title("Pitcher Strikeouts Live Projection — Powered by Public MLB API")

# Helper: Get player ID from name
def get_player_id(name):
    players = statsapi.lookup_player(name)
    if players:
        return players[0]['id']
    return None

# Helper: Get game logs and strikeouts for pitcher
def get_pitcher_strikeouts(player_id, num_games):
    # MLB uses YYYY-MM-DD for dates
    # Find today's date and roll back enough days to cover recent games
    from datetime import date, timedelta
    today = date.today()
    days_back = 180  # Up to 6 months for maximal flexibility
    start = today - timedelta(days=days_back)
    schedule = statsapi.schedule(
        start_date=start.strftime('%m/%d/%Y'),
        end_date=today.strftime('%m/%d/%Y'),
        player_id=player_id
    )

    # Filter only games where player has pitching stats
    pitch_logs = []
    for game in reversed(schedule):
        stats = game.get('pitching', [])
        for entry in stats:
            if entry.get('player_id') == player_id:
                pitch_logs.append({
                    'date': game['game_date'],
                    'opponent': game['opponent_name'],
                    'strikeouts': entry.get('note', entry.get('strikeOuts', None))
                })
    # Only keep most recent requested games with valid strikeout data
    logs = [log for log in pitch_logs if log['strikeouts'] is not None]
    return logs[-num_games:] if len(logs) >= num_games else logs

# --- Streamlit App ---
pitcher_name = st.text_input("Enter Pitcher's Name (e.g., Spencer Strider):")
num_games = st.slider("How many most recent games to analyze?", 3, 30, 10)
custom_line = st.number_input("Enter your Over/Under strikeout line (e.g., 6.5):", step=0.5, value=6.5)

if pitcher_name:
    player_id = get_player_id(pitcher_name)
    if player_id:
        logs = get_pitcher_strikeouts(player_id, num_games)
        if logs:
            df = pd.DataFrame(logs)
            df['strikeouts'] = pd.to_numeric(df['strikeouts'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna(subset=['strikeouts'])

            st.write(f"Last {len(df)} games for **{pitcher_name}**:")
            st.dataframe(df.sort_values('date')[['date', 'opponent', 'strikeouts']])

            avg_so = df['strikeouts'].mean()
            over = (df['strikeouts'] > custom_line).sum()
            under = (df['strikeouts'] < custom_line).sum()
            push = (df['strikeouts'] == custom_line).sum()
            total = len(df)
            prob_over = 100 * over / total if total else 0
            prob_under = 100 * under / total if total else 0

            st.markdown(f"""
            - **Average strikeouts:** `{avg_so:.2f}`
            - **Probability Over {custom_line}:** `{prob_over:.1f}%` ({over}/{total})
            - **Probability Under {custom_line}:** `{prob_under:.1f}%` ({under}/{total})
            - **Push (exact match):** `{push}` games
            """)

            if abs(prob_over - prob_under) < 5:
                st.info("No strong edge detected: probabilities nearly equal.")
            elif prob_over > prob_under:
                st.success(f"Best probability: **Over** ({prob_over:.1f}%)")
            else:
                st.success(f"Best probability: **Under** ({prob_under:.1f}%)")

            st.line_chart(df.set_index('date')['strikeouts'])
        else:
            st.warning(f"No MLB game logs with pitching stats found for '{pitcher_name}' in the last {num_games} games.")
    else:
        st.error(f"Could not find MLB pitcher named '{pitcher_name}'. Check spelling or try a different name.")

else:
    st.info("Enter a pitcher’s name and choose your settings to begin.")

    st.info("Upload your data CSV to start.")
