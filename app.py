import pandas as pd
import streamlit as st

st.title("Pitcher Strikeouts Probability Analyzer — Large Sample Mode")

def load_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='cp1252')
    # Drop index column if present
    if df.columns[0].startswith('Unnamed') or df.columns[0] == '':
        df = df.iloc[:, 1:]
    return df

uploaded_file = st.file_uploader("Upload your pitcher data CSV", type="csv")
if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.write("Data preview:")
    st.write(df.head())

    required_cols = ['pitcher_name', 'actual_strikeouts', 'date']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing columns in your CSV: {', '.join(missing)}")
    else:
        pitcher = st.selectbox("Select Pitcher", sorted(df['pitcher_name'].dropna().unique()))
        pitcher_data = df[df['pitcher_name'] == pitcher].copy()

        # Parse and sort by date
        pitcher_data['date'] = pd.to_datetime(pitcher_data['date'], errors='coerce')
        pitcher_data = pitcher_data.sort_values('date')

        st.write(f"Games for {pitcher}:")
        st.write(
            pitcher_data[['date', 'opponent'] + [c for c in ['actual_strikeouts'] if c in pitcher_data.columns]]
        )

        max_games = len(pitcher_data)
        default_games = min(20, max_games)
        num_games = st.slider(
            "How many most recent games to analyze?",
            min_value=3,
            max_value=max_games,
            value=default_games,
            step=1
        )
        recent_games = pitcher_data.tail(num_games)

        # User sets custom over/under line
        user_line = st.number_input(
            "Set your Over/Under strikeouts line (e.g., 5.5):",
            step=0.5,
            value=5.5
        )

        # Calculate
        so = pd.to_numeric(recent_games['actual_strikeouts'], errors='coerce').dropna()
        over_count = (so > user_line).sum()
        under_count = (so < user_line).sum()
        push_count = (so == user_line).sum()
        total_games = len(so)

        prob_over = over_count / total_games * 100 if total_games else 0
        prob_under = under_count / total_games * 100 if total_games else 0
        prob_push = push_count / total_games * 100 if total_games else 0

        if abs(prob_over - prob_under) < 5:
            recommendation = "No clear edge (chance is about 50/50)."
        elif prob_over > prob_under:
            recommendation = f"Best probability: **Over** ({prob_over:.1f}%)"
        else:
            recommendation = f"Best probability: **Under** ({prob_under:.1f}%)"

        st.subheader("Strikeout Projection & Probability (Larger Sample)")
        st.markdown(f"""
- Average strikeouts (*last {total_games} games*): **{so.mean():.2f}**
- Your line: **{user_line}**
- Over: **{over_count} times ({prob_over:.1f}%)**
- Under: **{under_count} times ({prob_under:.1f}%)**
- Push (exact): **{push_count} times ({prob_push:.1f}%)**
""")
        st.success(recommendation)

        st.line_chart(pd.DataFrame({
            'Strikeouts': so.values
        }, index=recent_games['date'].dt.strftime('%Y-%m-%d')))

        st.caption(
            "Adjust the games slider to use a larger or smaller sample for your projections — "
            "analyzing more games typically gives a more stable, trustworthy probability!"
        )

else:
    st.info("Upload your data CSV to start.")
