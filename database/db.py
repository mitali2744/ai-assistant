import sqlite3                       # built-in Python SQLite library
from utils.config import DB_PATH    # DB file path from config

def get_connection():
    # open and return a connection to the SQLite database file
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()          # open DB connection
    cursor = conn.cursor()           # cursor lets us run SQL commands

    # create users table to store login credentials
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # create tasks table to store all user tasks
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

    # add missing columns if upgrading from older DB version
    for col, definition in [
        ("user_id", "INTEGER NOT NULL DEFAULT 1"),   # link tasks to users
        ("priority", "TEXT DEFAULT 'medium'"),        # task priority level
        ("category", "TEXT DEFAULT 'general'"),       # subject category
        ("deadline", "TEXT DEFAULT NULL"),            # optional due date
        ("completed_at", "TIMESTAMP DEFAULT NULL"),   # completion timestamp
    ]:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # column already exists, skip silently

    conn.commit()   # save all changes to disk
    conn.close()    # close the DB connection
