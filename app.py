import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF

API_URL = st.secrets.get("api_url", "https://saas-back-v4.onrender.com")

st.title("Triphorium Energy Dashboard")

# Sidebar: Building Info
st.sidebar.header("Building Input")
building_type = st.sidebar.selectbox("Building Type", ["Office", "School", "Hospital", "Retail"])
address = st.sidebar.text_input("Building Address", "New York, NY")
floor_area = st.sidebar.number_input("Area (sqft)", value=10000)
occupancy_rate = st.sidebar.slider("Occupancy Rate", 0.0, 1.0, 0.85)
operation_hours = st.sidebar.slider("Operation Hours per Day", 0, 24, 10)

# Climate Zone Mapping
climate_zone = "4A - Mixed-Humid" if "NY" in address else "Unknown"
st.markdown(f"**Climate Zone**: {climate_zone}")

# Energy Trend
st.subheader("10-Year Energy Trends")

try:
    res = requests.get(f"{API_URL}/energy/data")
    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        df.columns = [col.lower() for col in df.columns]  # standardize
        st.write("Backend data columns:", df.columns)     # debug

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            st.line_chart(df[["electricity_kwh", "water_tons", "gas_m3", "co2_tons"]])
        else:
            st.error("❌ Missing 'timestamp' column in backend data.")
            st.stop()
    else:
        st.warning("Backend returned error. Using demo data.")
        raise ValueError("Backend returned non-200")
except:
    st.warning("Unable to connect to backend. Using demo data.")
    df = pd.DataFrame({
        "timestamp": pd.date_range("2015-01-01", "2024-12-01", freq="MS"),
        "electricity_kwh": [12000 + i*50 for i in range(120)],
        "water_tons": [300 + i*0.5 for i in range(120)],
        "gas_m3": [110 + i*0.3 for i in range(120)],
        "co2_tons": [round((12000 + i*50) * 0.00052, 2) for i in range(120)]
    })
    df.set_index("timestamp", inplace=True)
    st.line_chart(df[["electricity_kwh", "water_tons", "gas_m3", "co2_tons"]])

# ROI Summary
st.subheader("Financial Impact Summary")
cost = st.number_input("Investment Cost ($)", value=30000)
rate = st.number_input("Electricity Price ($/kWh)", value=0.18)
saving_kwh = df["electricity_kwh"].mean()
annual_saving = saving_kwh * rate
roi = (annual_saving / cost) * 100
payback = cost / annual_saving if annual_saving else None

st.metric("Annual Savings", f"${annual_saving:,.2f}")
st.metric("ROI", f"{roi:.1f}%")
st.metric("Payback Period", f"{payback:.1f} years")

# Suggestions
st.subheader("Operational Strategy Suggestions")
st.markdown("- Upgrade to high-efficiency HVAC")
st.markdown("- Add smart occupancy sensors")
st.markdown("- Implement energy analytics dashboard")
st.markdown("- Improve building envelope insulation")

# PDF Export
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Triphorium Energy Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Building Type: {building_type}", ln=True)
    pdf.cell(200, 10, txt=f"Climate Zone: {climate_zone}", ln=True)
    pdf.cell(200, 10, txt=f"Annual Savings: ${annual_saving:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"ROI: {roi:.1f}%", ln=True)
    pdf.cell(200, 10, txt=f"Payback Period: {payback:.1f} years", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Recommendations:\\n- HVAC upgrade\\n- Sensors\\n- Monitoring\\n- Insulation")
    return pdf

if st.button("Export PDF Report"):
    report = generate_pdf()
    report.output("triphorium_report.pdf")
    with open("triphorium_report.pdf", "rb") as f:
        st.download_button("📄 Download PDF", f, file_name="Triphorium_Energy_Report.pdf")

