import json
import os
from constants import SETTINGS_FILE, LEADERBOARD_FILE


def load_settings():
    default_settings = {
        "sound": True,
        "car_color": "original",
        "difficulty": "normal"
    }

    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings

    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
    except:
        save_settings(default_settings)
        return default_settings

    for key in default_settings:
        if key not in settings:
            settings[key] = default_settings[key]

    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        save_leaderboard([])
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    except:
        save_leaderboard([])
        return []


def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_score(name, score, distance, coins):
    data = load_leaderboard()

    data.append({
        "name": name,
        "score": score,
        "distance": int(distance),
        "coins": coins
    })

    data.sort(key=lambda x: x["score"], reverse=True)
    data = data[:10]

    save_leaderboard(data)