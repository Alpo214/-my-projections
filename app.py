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
            "How many most recent games
