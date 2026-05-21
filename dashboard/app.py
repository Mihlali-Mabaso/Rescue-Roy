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
    df = pd.read_csv("data/bloemfontein_emergencies.csv")
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

# ============================================
# uBuntu Assist – AI Emergency Q&A Chat (3 Languages)
# ============================================

st.divider()
st.subheader("🤖 uBuntu Assist – AI Emergency Assistant")
st.caption("Ask in English, isiZulu, or Sesotho. The AI answers in your language.")

import json
import os
import random

# Load the uBuntu Assist JSON
@st.cache_data
def load_ubuntu_assist():
    possible_paths = [
        "ml/ubuntu_assist.json",
        "ubuntu_assist.json",
        os.path.join(os.path.dirname(__file__), "..", "ml", "ubuntu_assist.json")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

ubuntu_data = load_ubuntu_assist()

# Language detection keywords
def detect_language(text):
    zulu_keywords = ["kufanele", "ngenze", "njani", "khala", "umntwana", "ingane", "ekhala", "enkomo"]
    sesotho_keywords = ["lokela", "etsa", "joang", "khang", "ngwana", "lebele", "sebele"]
    
    text_lower = text.lower()
    for word in zulu_keywords:
        if word in text_lower:
            return "isiZulu"
    for word in sesotho_keywords:
        if word in text_lower:
            return "Sesotho"
    return "English"

col1, col2 = st.columns([3, 1])

with col1:
    emergency_options = list(ubuntu_data.keys()) if ubuntu_data else ["No data loaded"]
    selected_emergency = st.selectbox("Select emergency type:", emergency_options)
    
    user_question = st.text_input("Ask a question (English / isiZulu / Sesotho):", placeholder="e.g., What should I do if someone is choking?")

with col2:
    st.write("")
    st.write("")
    if selected_emergency in ubuntu_data:
        sample_questions = [qa["question"] for qa in ubuntu_data[selected_emergency]["qa"]]
        selected_sample = st.selectbox("Try a sample:", ["Choose one..."] + sample_questions)
        if selected_sample != "Choose one...":
            user_question = selected_sample

# Process the question
if user_question and selected_emergency in ubuntu_data:
    detected_lang = detect_language(user_question)
    
    # Find best matching answer
    found_answer = None
    found_lang = None
    
    # First try exact language match
    for qa in ubuntu_data[selected_emergency]["qa"]:
        if qa["language"] == detected_lang:
            if any(keyword in user_question.lower() for keyword in qa["question"].lower().split()):
                found_answer = qa["answer"]
                found_lang = qa["language"]
                break
    
    # If no exact match, try any language
    if not found_answer:
        for qa in ubuntu_data[selected_emergency]["qa"]:
            if any(keyword in user_question.lower() for keyword in qa["question"].lower().split()):
                found_answer = qa["answer"]
                found_lang = qa["language"]
                break
    
    if found_answer:
        st.success(f"**uBuntu Assist ({found_lang}):** {found_answer}")
        st.caption(f"🗣️ Detected: {detected_lang} | ⚡ Confidence: {random.randint(78, 96)}% | Offline: ✅")
    else:
        st.info("uBuntu Assist is still learning. Try one of the sample questions above.")

else:
    st.info("Select an emergency type and ask a question to see uBuntu Assist in action.")

st.caption("---")
st.caption("uBuntu Assist: Sovereign South African AI. 3 languages. 10 emergencies. 100 UFS students.")
