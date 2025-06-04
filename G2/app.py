# app.py
import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(layout="wide")
st.title("📊 G2 SaaS Insights Dashboard")

excel_file = "G2_SaaS_Insights.xlsx"

if st.button("🕷️ Run Web Scraper"):
    with st.spinner("Scraping BigIdeasDB (please wait ~5 min)..."):
        result = subprocess.run(["python3", "scraper.py"], capture_output=True, text=True)
    if result.returncode == 0:
        st.success("✅ Scraping complete!")
    else:
        st.error("❌ Scraping failed!")
        st.text(result.stderr)

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    st.markdown("### ✅ Scraped Results")
    st.dataframe(df)

    st.download_button("📥 Download Excel", df.to_excel(index=False), file_name=excel_file)
else:
    st.info("No data file found. Click the button above to run the scraper.")
