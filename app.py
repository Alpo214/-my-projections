import pandas as pd
import streamlit as st

st.title("Pitcher Strikeouts Over/Under Analyzer")

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
    # Drop index column if present (like "Unnamed: 0")
    if df.columns[0].startswith('Unnamed') or df.columns[0] == '':
        df = df.iloc[:, 1:]
    return df

uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.write("Preview of your data:")
    st.write(df.head())

    # Validate required columns
    required_cols = ['pitcher_name', 'actual_strikeouts', 'date']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing columns in your CSV: {', '.join(missing)}")
    else:
        pitcher = st.selectbox("Select Pitcher", sorted(df['pitcher_name'].unique()))
        pitcher_data = df[df['pitcher_name'] == pitcher].copy()

        # Try to parse and sort dates for proper order
        pitcher_data['date'] = pd.to_datetime(pitcher_data['date'], errors='coerce')
        pitcher_data = pitcher_data.sort_values('date')

        st.write(f"Game log for {pitcher}:", pitcher_data[['date', 'actual_strikeouts']])

        max_games = min(10, len(pitcher_data))
        num_games = st.slider("Number of recent games to analyze", 1, len(pitcher_data), max_games)
        recent_games = pitcher_data.tail(num_games)

        # Custom over/under input
        over_under = st.number_input(
            "Enter your Over/Under projection line (e.g., 5.5):",
            step=0.5
        )

        so_vals = pd.to_numeric(recent_games['actual_strikeouts'], errors='coerce')
        # Compute results
        over_count = (so_vals > over_under).sum()
        under_count = (so_vals < over_under).sum()
        push_count = (so_vals == over_under).sum()
        pct_over = 100 * over_count / len(so_vals) if len(so_vals) else 0
        pct_under = 100 * under_count / len(so_vals) if len(so_vals) else 0
        pct_push = 100 * push_count / len(so_vals) if len(so_vals) else 0

        st.subheader("Custom Over/Under Analysis")
        st.write(f"Projections use last {num_games} games for {pitcher}.")
        st.table({
            "Stat": ["Times Over", "Times Under", "Exact Match (Push)", "Average Strikeouts", "Your Line"],
            "Value": [
                f"{over_count}  ({pct_over:.1f}%)",
                f"{under_count}  ({pct_under:.1f}%)",
                f"{push_count}  ({pct_push:.1f}%)",
                f"{so_vals.mean():.2f}",
                over_under
            ]
        })

        st.line_chart(recent_games.set_index('date')['actual_strikeouts'])

        st.caption("Change the number above to instantly update your over/under results.")

else:
    st.info("Upload your CSV to begin.")

