import sqlite3
from utils.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'general',
            deadline TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL
        )
    """)

    # Add new columns if upgrading from old schema
    for col, definition in [
        ("priority", "TEXT DEFAULT 'medium'"),
        ("category", "TEXT DEFAULT 'general'"),
        ("deadline", "TEXT DEFAULT NULL"),
        ("completed_at", "TIMESTAMP DEFAULT NULL"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # column already exists

    conn.commit()
    conn.close()
