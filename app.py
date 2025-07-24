import pandas as pd
import streamlit as st

st.title("PrizePicks Simple CSV Analyzer")

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
    return df

uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    df = load_csv(uploaded_file)
    # Always drop the first, unnamed index column
    if df.columns[0].startswith('Unnamed') or df.columns[0] == '':
        df = df.iloc[:, 1:]
    st.write("Preview of your data:", df.head())

    # Let user choose a stat column to analyze
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    if numeric_cols:
        stat = st.selectbox("Select a numeric stat to average:", numeric_cols)
        avg = pd.to_numeric(df[stat], errors='coerce').mean()
        st.write(f"Average {stat}: {avg:.2f}")
    else:
        st.warning("No numeric columns found to analyze.")

    # Always show the full table for clarity
    st.dataframe(df)
else:
    st.info("Please upload your data_template.csv file above.")
