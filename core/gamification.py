import json
import os
from datetime import datetime, date

XP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "xp_data.json")

LEVELS = [
    (0,    "Freshman"),
    (100,  "Sophomore"),
    (250,  "Junior"),
    (500,  "Senior"),
    (800,  "Graduate"),
    (1200, "Scholar"),
    (1800, "Academic Legend"),
]

BADGES = {
    "first_task":      ("First Step",        "Completed your first task!"),
    "streak_3":        ("On Fire",           "3-day completion streak!"),
    "streak_7":        ("Unstoppable",       "7-day streak — incredible!"),
    "early_bird":      ("Early Bird",        "Completed a task before its deadline!"),
    "deadline_crusher":("Deadline Crusher",  "Completed 5 high-priority tasks!"),
    "consistent":      ("Consistent Learner","Completed tasks 5 days in a row!"),
    "centurion":       ("Centurion",         "Reached 100 XP!"),
    "scholar":         ("Scholar",           "Reached Scholar level!"),
}

def _load():
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)
    return {"xp": 0, "streak": 0, "last_date": None, "badges": [], "completed_count": 0, "high_priority_done": 0}

def _save(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_level(xp):
    level_name = LEVELS[0][1]
    for threshold, name in LEVELS:
        if xp >= threshold:
            level_name = name
    return level_name

def add_xp(amount, reason=""):
    data = _load()
    old_xp = data["xp"]
    data["xp"] += amount
    new_level = get_level(data["xp"])
    old_level = get_level(old_xp)
    _save(data)

    msg = f"+{amount} XP ({reason}). Total: {data['xp']} XP | Level: {new_level}"
    if new_level != old_level:
        msg += f" 🎉 LEVEL UP! You are now a {new_level}!"
    return msg

def update_streak(priority=None, deadline=None):
    data = _load()
    today = date.today().isoformat()
    messages = []

    # Update streak
    if data["last_date"] == today:
        pass  # already counted today
    elif data["last_date"] == (date.today().replace(day=date.today().day - 1)).isoformat() if date.today().day > 1 else None:
        data["streak"] += 1
    else:
        data["streak"] = 1

    data["last_date"] = today
    data["completed_count"] = data.get("completed_count", 0) + 1

    if priority == "high":
        data["high_priority_done"] = data.get("high_priority_done", 0) + 1

    # Check badges
    new_badges = []
    if data["completed_count"] == 1 and "first_task" not in data["badges"]:
        data["badges"].append("first_task")
        new_badges.append(BADGES["first_task"])

    if data["streak"] >= 3 and "streak_3" not in data["badges"]:
        data["badges"].append("streak_3")
        new_badges.append(BADGES["streak_3"])

    if data["streak"] >= 7 and "streak_7" not in data["badges"]:
        data["badges"].append("streak_7")
        new_badges.append(BADGES["streak_7"])

    if data["high_priority_done"] >= 5 and "deadline_crusher" not in data["badges"]:
        data["badges"].append("deadline_crusher")
        new_badges.append(BADGES["deadline_crusher"])

    if data["xp"] >= 100 and "centurion" not in data["badges"]:
        data["badges"].append("centurion")
        new_badges.append(BADGES["centurion"])

    if get_level(data["xp"]) == "Scholar" and "scholar" not in data["badges"]:
        data["badges"].append("scholar")
        new_badges.append(BADGES["scholar"])

    _save(data)

    if data["streak"] > 1:
        messages.append(f"🔥 {data['streak']}-day streak!")
    for name, desc in new_badges:
        messages.append(f"🏅 Badge unlocked: {name} — {desc}")

    return " ".join(messages)

def get_status():
    data = _load()
    level = get_level(data["xp"])
    # Find next level
    next_threshold = None
    for threshold, name in LEVELS:
        if data["xp"] < threshold:
            next_threshold = threshold
            break
    progress = f"{data['xp']} XP"
    if next_threshold:
        progress += f" / {next_threshold} XP to next level"

    badge_names = [BADGES[b][0] for b in data["badges"] if b in BADGES]
    badge_str = ", ".join(badge_names) if badge_names else "None yet"

    return (
        f"Level: {level} | {progress} | "
        f"Streak: {data['streak']} day(s) | "
        f"Tasks completed: {data['completed_count']} | "
        f"Badges: {badge_str}"
    )
