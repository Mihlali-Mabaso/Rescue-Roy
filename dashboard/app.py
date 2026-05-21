# Streamlit dashboard code
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Rescue Roy – Bloemfontein Emergency Dashboard", layout="wide")
st.title("🚑 Rescue Roy – Community Safety Intelligence Dashboard")
st.subheader("📊 Bloemfontein Real-Time Emergency Overview (Mock Data)")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("bloemfontein_emergencies.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Emergencies (180 days)", len(df))
col2.metric("Responder Acceptance Rate", f"{df['responder_accepted'].mean()*100:.1f}%")
col3.metric("Avg Response Time (when accepted)", f"{df[df['responder_accepted']]['response_time_sec'].mean():.0f}s")
col4.metric("Voice-Activated Emergencies", f"{df['voice_activated'].mean()*100:.1f}%")

# --- Map ---
st.subheader("📍 Emergency Heatmap (Bloemfontein)")
m = folium.Map(location=[-29.1195, 26.2175], zoom_start=12)
for _, row in df.iterrows():
    color = "red" if row["responder_accepted"] else "orange"
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=3,
        color=color,
        fill=True,
        fillOpacity=0.6,
        popup=f"{row['emergency_type']} | {row['neighborhood']} | {row['language']}"
    ).add_to(m)
st_folium(m, width=800, height=500)

# --- Charts Row ---
col1, col2 = st.columns(2)

with col1:
    # Emergency type distribution
    fig = px.pie(df, names="emergency_type", title="Emergency Types")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Response time by neighborhood
    accepted = df[df["responder_accepted"]]
    fig = px.bar(
        accepted.groupby("neighborhood")["response_time_sec"].mean().reset_index(),
        x="neighborhood", y="response_time_sec",
        title="Avg Response Time by Neighborhood (seconds)"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Language & Outcome ---
col1, col2 = st.columns(2)

with col1:
    lang_counts = df["language"].value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]
    fig = px.bar(lang_counts, x="Language", y="Count", title="Language Usage")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    outcome_counts = df["outcome"].value_counts().reset_index()
    outcome_counts.columns = ["Outcome", "Count"]
    fig = px.bar(outcome_counts, x="Outcome", y="Count", title="Emergency Outcomes")
    st.plotly_chart(fig, use_container_width=True)

# --- Raw Data (optional) ---
if st.checkbox("Show raw data"):
    st.dataframe(df)
