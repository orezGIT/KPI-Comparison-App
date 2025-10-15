# kpi_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Weekly KPI Comparison", layout="wide")

st.title("📊 Weekly KPI Comparison Dashboard")

# --- Upload CSVs ---
st.sidebar.header("Upload CSV files")
week1_file = st.sidebar.file_uploader("Upload Week 1 CSV", type=["csv"])
week2_file = st.sidebar.file_uploader("Upload Week 2 CSV", type=["csv"])

if week1_file and week2_file:
    # --- Load Data ---
    df_week1 = pd.read_csv(week1_file, parse_dates=["date"])
    df_week2 = pd.read_csv(week2_file, parse_dates=["date"])

    # --- Align columns ---
    common_cols = ["date", "active_users", "new_signups", "retention_rate", 
                   "sessions", "avg_session_time", "conversion_rate", "revenue", "CAC"]
    df_week1 = df_week1[common_cols].copy()
    df_week2 = df_week2[common_cols].copy()

    # --- Aggregate KPIs for the week ---
    week1_summary = df_week1[common_cols[1:]].sum(numeric_only=True).to_frame().T
    week2_summary = df_week2[common_cols[1:]].sum(numeric_only=True).to_frame().T

    week1_summary["week"] = "Week 1"
    week2_summary["week"] = "Week 2"

    # --- Side-by-side KPI charts ---
    st.subheader("📈 Key KPIs Comparison")
    kpis = ["active_users", "new_signups", "retention_rate", "sessions", 
            "avg_session_time", "conversion_rate", "revenue", "CAC"]

    col1, col2 = st.columns(2)
    for kpi in kpis:
        fig = px.bar(pd.concat([week1_summary, week2_summary]), x="week", y=kpi,
                     text=kpi, title=f"{kpi.replace('_',' ').title()} Comparison")
        col1.plotly_chart(fig, use_container_width=True)

    # --- Compute % change ---
    comparison = pd.DataFrame()
    comparison["KPI"] = kpis
    comparison["Week1"] = week1_summary[kpis].values[0]
    comparison["Week2"] = week2_summary[kpis].values[0]
    comparison["% Change"] = ((comparison["Week2"] - comparison["Week1"]) / comparison["Week1"] * 100).round(2)

    st.subheader("📊 KPI Comparison Table")
    st.dataframe(comparison)

    # --- Plain-English summary ---
    st.subheader("📝 Summary")
    summary_lines = []
    for _, row in comparison.iterrows():
        if row["% Change"] > 0:
            line = f"{row['KPI'].replace('_',' ').title()} increased by {row['% Change']}% from Week 1 to Week 2."
        elif row["% Change"] < 0:
            line = f"{row['KPI'].replace('_',' ').title()} decreased by {abs(row['% Change'])}% from Week 1 to Week 2."
        else:
            line = f"{row['KPI'].replace('_',' ').title()} remained unchanged."
        summary_lines.append(line)
    st.write("\n".join(summary_lines))

    # --- Download comparison table ---
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(comparison)
    st.download_button(
        label="⬇️ Download Comparison CSV",
        data=csv_data,
        file_name="kpi_comparison.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload both Week 1 and Week 2 CSV files to view the dashboard.")
