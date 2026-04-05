import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, get_connection
from core.assistant_brain import process_query, set_speak_callback
from core.command_handler import get_task_counts, get_due_today
from core.gamification import get_status
from utils.config import ASSISTANT_NAME

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "aria_secret_key_2026")

set_speak_callback(lambda text: None)

@app.before_request
def ensure_db():
    try:
        init_db()
    except Exception:
        pass


    return session.get("user_id", 1)

def get_username():
    return session.get("username", "User")

# ── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    mode = request.form.get("mode", "login")
    message = None
    error = False

    if request.method == "POST" and "username" in request.form:
        username = request.form["username"].strip().lower()
        password = request.form["password"].strip()

        if mode == "register":
            conn = get_connection()
            existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
            if existing:
                conn.close()
                message = "Username already taken. Try another."
                error = True
            else:
                pw_hash = generate_password_hash(password)
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
                conn.commit()
                conn.close()
                message = f"Account created! Welcome, {username}. Please login."
                mode = "login"
        else:
            conn = get_connection()
            user = conn.execute("SELECT id, password_hash FROM users WHERE username=?", (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                return redirect(url_for("index"))
            else:
                message = "Invalid username or password."
                error = True

    return render_template("login.html", mode=mode, message=message, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Main routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", assistant_name=ASSISTANT_NAME, username=get_username())

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"type": "text", "response": "Please login first."})

    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"type": "text", "response": "Please type something."})

    user_id = get_user_id()
    response = process_query(user_msg, user_id=user_id)

    if response == "PROMPT_TASK":
        response = "Sure! What task would you like to add? Example: add task study ML high category ai 2026-04-01"

    if response and response.startswith("IMAGE:"):
        return jsonify({"type": "image", "image": response[6:]})

    return jsonify({"type": "text", "response": response})

@app.route("/status")
def status():
    if "user_id" not in session:
        return jsonify({"pending": 0, "completed": 0, "due_today": [], "xp_status": ""})
    user_id = get_user_id()
    counts = get_task_counts(user_id=user_id)
    due = get_due_today(user_id=user_id)
    xp_status = get_status()
    return jsonify({
        "pending": counts.get("pending", 0),
        "completed": counts.get("completed", 0),
        "due_today": [{"id": t[0], "task": t[1], "priority": t[2]} for t in due],
        "xp_status": xp_status,
        "username": get_username()
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
