import os

ASSISTANT_NAME = "Aria"

# Use /tmp on Linux (Vercel), local path on Windows
if os.name == "nt":  # Windows
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assistant.db")
else:
    DB_PATH = os.environ.get("DB_PATH", "/tmp/assistant.db")

VOICE_MODE = True
