from database.db import get_connection

def _init(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS study_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS group_members (group_id INTEGER, username TEXT, PRIMARY KEY (group_id, username))")
    conn.execute("CREATE TABLE IF NOT EXISTS group_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER NOT NULL, task TEXT NOT NULL, assigned_to TEXT DEFAULT NULL, status TEXT DEFAULT 'pending', priority TEXT DEFAULT 'medium', created_by TEXT NOT NULL)")
    conn.commit()

def register_user(username):
    username = username.strip().lower()
    conn = get_connection()
    _init(conn)
    try:
        conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        conn.close()
        return f"User '{username}' registered! Welcome to Aria."
    except Exception:
        conn.close()
        return f"Username '{username}' already taken."

def create_group(group_name, username):
    group_name = group_name.strip().lower()
    conn = get_connection()
    _init(conn)
    try:
        conn.execute("INSERT INTO study_groups (name) VALUES (?)", (group_name,))
        gid = conn.execute("SELECT id FROM study_groups WHERE name=?", (group_name,)).fetchone()[0]
        conn.execute("INSERT INTO group_members (group_id, username) VALUES (?, ?)", (gid, username.lower()))
        conn.commit()
        conn.close()
        return f"Study group '{group_name}' created!"
    except Exception:
        conn.close()
        return f"Group '{group_name}' already exists."

def join_group(group_name, username):
    group_name = group_name.strip().lower()
    conn = get_connection()
    _init(conn)
    group = conn.execute("SELECT id FROM study_groups WHERE name=?", (group_name,)).fetchone()
    if not group:
        conn.close()
        return f"Group '{group_name}' not found."
    try:
        conn.execute("INSERT INTO group_members (group_id, username) VALUES (?, ?)", (group[0], username.lower()))
        conn.commit()
        conn.close()
        return f"You joined group '{group_name}'!"
    except Exception:
        conn.close()
        return f"Already a member of '{group_name}'."

def add_group_task(group_name, task, created_by, assigned_to=None, priority="medium"):
    group_name = group_name.strip().lower()
    conn = get_connection()
    _init(conn)
    group = conn.execute("SELECT id FROM study_groups WHERE name=?", (group_name,)).fetchone()
    if not group:
        conn.close()
        return f"Group '{group_name}' not found."
    conn.execute("INSERT INTO group_tasks (group_id,task,created_by,assigned_to,priority) VALUES (?,?,?,?,?)", (group[0], task.strip(), created_by.lower(), assigned_to, priority))
    conn.commit()
    conn.close()
    return f"Task '{task}' added to group '{group_name}'" + (f", assigned to {assigned_to}." if assigned_to else ".")

def show_group_tasks(group_name):
    group_name = group_name.strip().lower()
    conn = get_connection()
    _init(conn)
    group = conn.execute("SELECT id FROM study_groups WHERE name=?", (group_name,)).fetchone()
    if not group:
        conn.close()
        return f"Group '{group_name}' not found."
    rows = conn.execute("SELECT id,task,status,priority,assigned_to FROM group_tasks WHERE group_id=? ORDER BY id", (group[0],)).fetchall()
    conn.close()
    if not rows:
        return f"No tasks in group '{group_name}' yet."
    lines = [f"Group '{group_name}' tasks:"]
    for r in rows:
        line = f"  {r[0]}. [{r[3].upper()}] {r[1]} ({r[2]})"
        if r[4]:
            line += f" -> {r[4]}"
        lines.append(line)
    return "\n".join(lines)

def complete_group_task(task_id):
    conn = get_connection()
    _init(conn)
    conn.execute("UPDATE group_tasks SET status='completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return f"Group task {task_id} marked as completed!"

def group_productivity(group_name):
    group_name = group_name.strip().lower()
    conn = get_connection()
    _init(conn)
    group = conn.execute("SELECT id FROM study_groups WHERE name=?", (group_name,)).fetchone()
    if not group:
        conn.close()
        return f"Group '{group_name}' not found."
    rows = conn.execute("SELECT status, COUNT(*) FROM group_tasks WHERE group_id=? GROUP BY status", (group[0],)).fetchall()
    members = conn.execute("SELECT username FROM group_members WHERE group_id=?", (group[0],)).fetchall()
    conn.close()
    data = {r[0]: r[1] for r in rows}
    total = sum(data.values())
    completed = data.get("completed", 0)
    score = (completed / total * 100) if total > 0 else 0
    return f"Group '{group_name}' | Members: {', '.join([m[0] for m in members])}\nTasks: {completed}/{total} | Score: {score:.1f}%"

def list_groups():
    conn = get_connection()
    _init(conn)
    rows = conn.execute("SELECT name FROM study_groups").fetchall()
    conn.close()
    if not rows:
        return "No study groups yet. Create one with: create group <name>"
    return "Study groups: " + ", ".join([r[0] for r in rows])
