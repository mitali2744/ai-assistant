import sqlite3
from utils.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tasks table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'general',
            deadline TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL
        )
    """)

    # Add user_id column if upgrading
    for col, definition in [
        ("user_id", "INTEGER NOT NULL DEFAULT 1"),
        ("priority", "TEXT DEFAULT 'medium'"),
        ("category", "TEXT DEFAULT 'general'"),
        ("deadline", "TEXT DEFAULT NULL"),
        ("completed_at", "TIMESTAMP DEFAULT NULL"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
