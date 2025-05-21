import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import google.generativeai as genai
import os

# --- Gemini API Setup ---
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyC8pJl8WBwpa_T5zMPMD5YcYVZWOyVFMZQ")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Page Config ---
st.set_page_config(page_title="IoT Wearable Health Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("/content/iot_worker_conditions_dataset.csv")

df = load_data()

# --- Title ---
st.title("📡 IoT Wearable Dashboard - Health & Environment Monitor")

# --- KPIs ---
st.subheader("📈 Real-Time KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Temp", f"{df['Temperature (°C)'].mean():.1f} °C")
col2.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.1f} %")
col3.metric("Avg AQI", f"{df['AQI'].mean():.0f}")
col4.metric("Avg HR", f"{df['Heart Rate (bpm)'].mean():.0f} bpm")

# --- Charts ---
st.subheader("📊 Sensor Trends Over Time")
st.line_chart(df[["Temperature (°C)", "Humidity (%)", "Sound (dB)", "AQI"]])

# --- Alerts ---
st.subheader("⚠️ Alerts")
alerts = df[
    (df["Temperature (°C)"] > 37) |
    (df["AQI"] > 150) |
    (df["Sound (dB)"] > 85) |
    (df["Heart Rate (bpm)"] > 120) |
    (df["SpO2 (%)"] < 94)
]
if not alerts.empty:
    st.error("🚨 Warning: Unsafe conditions detected!")
    st.dataframe(alerts)
else:
    st.success("✅ All monitored values are within safe limits.")

# --- Map View ---
st.subheader("🗺️ Location Map")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=df["Latitude"].mean(),
        longitude=df["Longitude"].mean(),
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[Longitude, Latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=40,
        ),
    ],
    tooltip={"text": "Timestamp: {Timestamp}\nTemp: {Temperature (°C)}°C\nHR: {Heart Rate (bpm)} bpm\nAQI: {AQI}"}
))

# --- Gemini Summary ---
st.subheader("🤖 Gemini AI Summary")
if st.button("🧠 Generate AI Summary"):
    summary_prompt = f"""
    Analyze the following real-time sensor data from a wearable IoT device:
    - Avg Temp: {df['Temperature (°C)'].mean():.1f} °C
    - Avg Humidity: {df['Humidity (%)'].mean():.1f} %
    - Avg AQI: {df['AQI'].mean():.0f}
    - Avg Sound: {df['Sound (dB)'].mean():.1f} dB
    - Avg Heart Rate: {df['Heart Rate (bpm)'].mean():.0f} bpm
    - Avg SpO2: {df['SpO2 (%)'].mean():.1f} %

    Provide a short safety summary and list any health or environmental risks.
    """
    response = model.generate_content(summary_prompt)
    st.write(response.text)

# --- Gemini Chat ---
st.subheader("💬 Ask Gemini")
user_q = st.text_input("Ask a question about the data:")
if user_q:
    response = model.generate_content(f"Data: {df.to_dict()}. Question: {user_q}")
    st.info("Gemini Says:")
    st.write(response.text)

# --- Footer ---
st.caption("Built with ❤️ using Streamlit and Gemini API")
