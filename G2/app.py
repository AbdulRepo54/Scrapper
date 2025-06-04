# app.py
import streamlit as st
import pandas as pd
import os
import subprocess
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📊 G2 SaaS Insights Dashboard")

excel_file = "G2_SaaS_Insights.xlsx"

# Button to run the scraper
if st.button("🕷️ Run Web Scraper"):
    with st.spinner("Scraping BigIdeasDB (please wait ~5 min)..."):
        result = subprocess.run(["python", "scraper.py"], capture_output=True, text=True)
    if result.returncode == 0:
        st.success("✅ Scraping complete!")
    else:
        st.error("❌ Scraping failed!")
        st.text(result.stderr)

# Load and display Excel file if available
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    st.markdown("### ✅ Scraped Results")
    st.dataframe(df)

    # Fix download using BytesIO
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name="G2_SaaS_Insights.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No data file found. Click the button above to run the scraper.")
