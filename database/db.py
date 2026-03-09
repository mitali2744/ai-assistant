import sqlite3

conn = sqlite3.connect("assistant.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")