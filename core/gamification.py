import json                  # to read/write XP data as JSON
import os                   # for file path operations
from datetime import datetime, date   # date used for streak tracking

# absolute path to xp_data.json — goes up one level from core/ to project root
XP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "xp_data.json")

# XP thresholds and level names — (min_xp, level_name)
LEVELS = [
    (0,    "Freshman"),
    (100,  "Sophomore"),
    (250,  "Junior"),
    (500,  "Senior"),
    (800,  "Graduate"),
    (1200, "Scholar"),
    (1800, "Academic Legend"),
]

# badge definitions — key: (display_name, description)
BADGES = {
    "first_task":       ("First Step",         "Completed your first task!"),
    "streak_3":         ("On Fire",            "3-day completion streak!"),
    "streak_7":         ("Unstoppable",        "7-day streak — incredible!"),
    "early_bird":       ("Early Bird",         "Completed a task before its deadline!"),
    "deadline_crusher": ("Deadline Crusher",   "Completed 5 high-priority tasks!"),
    "consistent":       ("Consistent Learner", "Completed tasks 5 days in a row!"),
    "centurion":        ("Centurion",          "Reached 100 XP!"),
    "scholar":          ("Scholar",            "Reached Scholar level!"),
}

def _load():
    # load XP data from JSON file; return default values if file doesn't exist yet
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            return json.load(f)   # parse JSON into Python dict
    # default starting state for a new user
    return {"xp": 0, "streak": 0, "last_date": None, "badges": [], "completed_count": 0, "high_priority_done": 0}

def _save(data):
    # write the updated XP data dict back to the JSON file
    with open(XP_FILE, "w") as f:
        json.dump(data, f, indent=2)   # indent=2 makes it human-readable

def get_level(xp):
    # find the highest level the user has reached based on their XP
    level_name = LEVELS[0][1]   # start at lowest level (Freshman)
    for threshold, name in LEVELS:
        if xp >= threshold:     # keep updating as XP passes each threshold
            level_name = name
    return level_name

def add_xp(amount, reason=""):
    # add XP to user's total, detect level up, save, and return message
    data = _load()
    old_xp = data["xp"]              # save old XP to detect level change
    data["xp"] += amount             # add the new XP
    new_level = get_level(data["xp"])  # check new level
    old_level = get_level(old_xp)      # check old level
    _save(data)                        # persist to file

    msg = f"+{amount} XP ({reason}). Total: {data['xp']} XP | Level: {new_level}"
    if new_level != old_level:         # if level changed, add celebration message
        msg += f" 🎉 LEVEL UP! You are now a {new_level}!"
    return msg

def update_streak(priority=None, deadline=None):
    # update daily streak counter and check if any badges should be awarded
    data = _load()
    today = date.today().isoformat()   # get today's date as string e.g. "2026-04-05"
    messages = []

    # streak logic: if last activity was yesterday, increment; else reset to 1
    if data["last_date"] == today:
        pass   # already updated today, don't double count
    elif data["last_date"] == (date.today().replace(day=date.today().day - 1)).isoformat() if date.today().day > 1 else None:
        data["streak"] += 1   # consecutive day — extend streak
    else:
        data["streak"] = 1    # streak broken — reset to 1

    data["last_date"] = today                                      # update last activity date
    data["completed_count"] = data.get("completed_count", 0) + 1  # increment total tasks done

    if priority == "high":
        # track how many high-priority tasks completed (for Deadline Crusher badge)
        data["high_priority_done"] = data.get("high_priority_done", 0) + 1

    # check each badge condition and award if not already earned
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

    _save(data)   # save updated data with new badges and streak

    # build return message
    if data["streak"] > 1:
        messages.append(f"🔥 {data['streak']}-day streak!")
    for name, desc in new_badges:
        messages.append(f"🏅 Badge unlocked: {name} — {desc}")

    return " ".join(messages)

def get_status():
    # return a formatted string showing level, XP progress, streak, and badges
    data = _load()
    level = get_level(data["xp"])

    # find the XP needed for the next level
    next_threshold = None
    for threshold, name in LEVELS:
        if data["xp"] < threshold:
            next_threshold = threshold
            break   # stop at first level not yet reached

    progress = f"{data['xp']} XP"
    if next_threshold:
        progress += f" / {next_threshold} XP to next level"   # show progress toward next level

    # get display names of earned badges
    badge_names = [BADGES[b][0] for b in data["badges"] if b in BADGES]
    badge_str = ", ".join(badge_names) if badge_names else "None yet"

    return (
        f"Level: {level} | {progress} | "
        f"Streak: {data['streak']} day(s) | "
        f"Tasks completed: {data['completed_count']} | "
        f"Badges: {badge_str}"
    )
