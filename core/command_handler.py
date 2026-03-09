import sqlite3

def add_task(task):
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

    return "Task added successfully"


def show_tasks():
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()

    cursor.execute("SELECT task FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    if tasks:
        return "Your tasks are " + ", ".join([t[0] for t in tasks])
    else:
        return "You have no tasks"