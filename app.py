import pandas as pd
import streamlit as st

st.title("Pitcher Strikeouts Projection App")

def load_csv(uploaded_file):
    # Try multiple encodings for compatibility
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

uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.write("Preview of your data:")
    st.write(df.head())

    # Ensure column names are correct
    required_cols = ['pitcher_name', 'actual_strikeouts', 'prizepicks_line', 'date', 'opponent']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing columns in your CSV: {', '.join(missing)}")
    else:
        # Pitcher dropdown
        pitcher = st.selectbox("Select Pitcher", sorted(df['pitcher_name'].unique()))
        pitcher_data = df[df['pitcher_name'] == pitcher].copy()

        # Sort by date (assumes date format MM/DD/YYYY or similar)
        pitcher_data['date'] = pd.to_datetime(pitcher_data['date'], errors='coerce')
        pitcher_data = pitcher_data.sort_values('date')

        st.write(f"Game log for {pitcher}:", pitcher_data[['date', 'opponent', 'actual_strikeouts', 'prizepicks_line']])

        # How many recent games to use for projection?
        max_games = min(10, len(pitcher_data))
        num_games = st.slider("Number of recent games for projection", 1, len(pitcher_data), max_games)
        recent_games = pitcher_data.tail(num_games)

        # Calculate projections
        strikeouts = pd.to_numeric(recent_games['actual_strikeouts'], errors='coerce')
        line_vals = pd.to_numeric(recent_games['prizepicks_line'], errors='coerce')
        avg_so = strikeouts.mean()
        avg_line = line_vals.mean()
        diff = avg_so - avg_line

        # Show results
        st.subheader("Projection Results")
        st.write(f"**Average strikeouts ({num_games} most recent games):** {avg_so:.2f}")
        st.write(f"**Average PrizePicks line ({num_games} games):** {avg_line:.2f}")
        st.write(f"**Difference (Proj - Line):** {diff:+.2f}")

        # Optional: Visualize strikeout trend
        st.line_chart(recent_games.set_index('date')['actual_strikeouts'])

else:
    st.info("Upload your CSV to begin.")

