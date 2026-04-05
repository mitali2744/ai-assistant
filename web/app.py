import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify
from database.db import init_db
from core.assistant_brain import process_query, set_speak_callback
from core.command_handler import get_task_counts, get_due_today
from core.gamification import get_status
from utils.config import ASSISTANT_NAME

app = Flask(__name__)

set_speak_callback(lambda text: None)
init_db()

@app.route("/")
def index():
    return render_template("index.html", assistant_name=ASSISTANT_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"response": "Please type something."})
    response = process_query(user_msg)
    if response == "PROMPT_TASK":
        response = "Sure! What task would you like to add? You can say something like: 'add task complete ML assignment high category ai 2026-04-01'"
    if response and response.startswith("IMAGE:"):
        img_b64 = response[6:]
        return jsonify({"type": "image", "image": img_b64})
    if response and response.startswith("TABLE:"):
        return jsonify({"type": "table", "html": response[6:]})
    return jsonify({"type": "text", "response": response})

@app.route("/status")
def status():
    counts = get_task_counts()
    due = get_due_today()
    xp_status = get_status()
    return jsonify({
        "pending": counts.get("pending", 0),
        "completed": counts.get("completed", 0),
        "due_today": [{"id": t[0], "task": t[1], "priority": t[2]} for t in due],
        "xp_status": xp_status
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
