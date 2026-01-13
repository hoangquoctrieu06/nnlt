# history.py
import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_session(exercise_name, data):
    history = load_history()
    
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if exercise_name not in history:
        history[exercise_name] = []
    
    accuracy = round(data["good_reps"] / data["reps"] * 100, 1) if data["reps"] > 0 else 0
    
    history[exercise_name].append({
        "date": date_str,
        "reps": data["reps"],
        "good_reps": data["good_reps"],
        "wrong_reps": data["wrong_reps"],
        "accuracy": accuracy,
        "avg_angle": data["avg_angle"]
    })
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def get_history(exercise_name):
    return load_history().get(exercise_name, [])