# Generate Bloemfontein mock data
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Bloemfontein neighborhoods
neighborhoods = {
    "CBD": {"lat": -29.1195, "lon": 26.2175, "weight": 0.20},
    "Mangaung": {"lat": -29.1582, "lon": 26.2301, "weight": 0.25},
    "Botshabelo": {"lat": -29.2408, "lon": 26.7257, "weight": 0.15},
    "Thaba Nchu": {"lat": -29.2094, "lon": 26.8345, "weight": 0.10},
    "Heuwelsig": {"lat": -29.1053, "lon": 26.1935, "weight": 0.10},
    "Fichardtpark": {"lat": -29.1174, "lon": 26.1655, "weight": 0.10},
    "Universitas": {"lat": -29.1090, "lon": 26.1770, "weight": 0.10}
}

emergency_types = ["Choking", "Bleeding", "Burns", "Cardiac", "Seizure", "Allergic Reaction", "Breathing Difficulty", "Stroke", "Fracture", "Labour"]

languages = ["English", "isiZulu", "Sesotho"]
language_weights = [0.20, 0.35, 0.45]

responder_accept_rates = {
    "CBD": 0.70,
    "Heuwelsig": 0.80,
    "Fichardtpark": 0.85,
    "Universitas": 0.75,
    "Mangaung": 0.40,
    "Botshabelo": 0.30,
    "Thaba Nchu": 0.20
}

# Generate 500 emergencies over 180 days
n_emergencies = 500
start_date = datetime.now() - timedelta(days=180)
data = []

for _ in range(n_emergencies):
    # Choose neighborhood by weight
    hood = random.choices(list(neighborhoods.keys()), weights=[n["weight"] for n in neighborhoods.values()])[0]
    lat = neighborhoods[hood]["lat"] + np.random.normal(0, 0.001)
    lon = neighborhoods[hood]["lon"] + np.random.normal(0, 0.001)
    
    # Emergency type
    etype = random.choice(emergency_types)
    
    # Date/time - more in evenings (18:00-22:00) and weekends
    day_offset = random.randint(0, 180)
    # FIX: Use int() for the hour selection
    hour = int(np.random.choice([8,9,10,11,12,13,14,15,16,17,18,19,20,21,22], p=[0.04,0.04,0.04,0.04,0.06,0.06,0.06,0.06,0.06,0.08,0.10,0.10,0.10,0.08,0.08]))
    
    # FIX: Convert hour to int when passing to timedelta
    ts = start_date + timedelta(days=day_offset, hours=hour)
    
    # Language
    lang = random.choices(languages, weights=language_weights)[0]
    
    # Responder acceptance & response time
    accept_rate = responder_accept_rates[hood]
    responder_accepted = random.random() < accept_rate
    response_time_sec = -1 if not responder_accepted else int(np.random.gamma(2, 30))
    if response_time_sec > 600:
        response_time_sec = 600
    
    # Outcome
    if responder_accepted:
        outcome = random.choices(["Resolved by Responder", "Resolved by EMS", "Resolved by Self"], weights=[0.60, 0.30, 0.10])[0]
    else:
        outcome = random.choices(["Resolved by EMS", "Resolved by Self"], weights=[0.70, 0.30])[0]
    
    # Voice activation
    voice_activated = random.random() < 0.40
    
    data.append({
        "timestamp": ts.isoformat(),
        "neighborhood": hood,
        "lat": lat,
        "lon": lon,
        "emergency_type": etype,
        "language": lang,
        "responder_accepted": responder_accepted,
        "response_time_sec": response_time_sec,
        "outcome": outcome,
        "voice_activated": voice_activated
    })

df = pd.DataFrame(data)
df.to_csv("bloemfontein_emergencies.csv", index=False)
print(f"✅ Generated {len(df)} emergencies for Bloemfontein.")
print(f"CSV saved as: bloemfontein_emergencies.csv")
