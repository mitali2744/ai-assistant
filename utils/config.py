import os

ASSISTANT_NAME = "Aria"
DB_PATH = os.environ.get("DB_PATH", os.path.join("/tmp", "assistant.db"))
VOICE_MODE = True  # Set to False to use text-only mode
