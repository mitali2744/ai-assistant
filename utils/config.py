import os   # used to detect OS and build file paths

ASSISTANT_NAME = "Aria"   # name shown in the UI

# set DB path based on operating system
# on Windows (os.name == "nt"): use local file next to project root
# on Linux/Vercel: use /tmp which is the only writable directory
if os.name == "nt":
    # __file__ = this config.py file, go up one level (..) to project root
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assistant.db")
else:
    # on Vercel serverless, /tmp is the only writable folder
    DB_PATH = os.environ.get("DB_PATH", "/tmp/assistant.db")

VOICE_MODE = True   # enable voice input/output features
