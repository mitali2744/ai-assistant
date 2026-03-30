from database.db import get_connection
from datetime import datetime
from core.gamification import add_xp, update_streak

def add_task(task, priority="medium", category="general", deadline=None):
    task = task.strip()
    if not task:
        return "Please provide a task name."
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (task, priority, category, deadline) VALUES (?, ?, ?, ?)",
        (task, priority.lower(), category.lower(), deadline)
    )
    conn.commit()
    conn.close()
    msg = f"Task '{task}' added with {priority} priority"
    if category != "general":
        msg += f" under {category}"
    if deadline:
        msg += f", due on {deadline}"
    add_xp(5, "added a task")
    return msg + "."

def show_tasks(category=None, priority=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, task, status, priority, category, deadline FROM tasks"
    filters, params = [], []
    if category:
        filters.append("category=?")
        params.append(category.lower())
    if priority:
        filters.append("priority=?")
        params.append(priority.lower())
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC"
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    if not tasks:
        return "You have no tasks right now."
    lines = []
    for t in tasks:
        line = f"{t[0]}. [{t[3].upper()}] {t[1]} ({t[2]})"
        if t[4] != "general":
            line += f" | {t[4]}"
        if t[5]:
            line += f" | due: {t[5]}"
        lines.append(line)
    return "Your tasks:\n" + "\n".join(lines)

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT priority FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    priority = row[0] if row else "medium"
    cursor.execute(
        "UPDATE tasks SET status='completed', completed_at=? WHERE id=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id)
    )
    conn.commit()
    conn.close()

    xp_amount = {"high": 30, "medium": 20, "low": 10}.get(priority, 20)
    xp_msg = add_xp(xp_amount, f"completed {priority} priority task")
    streak_msg = update_streak(priority=priority)

    msg = f"Task {task_id} marked as completed! Great work!"
    if streak_msg:
        msg += " " + streak_msg
    msg += " | " + xp_msg
    return msg

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return f"Task {task_id} deleted."

def get_task_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def get_due_today():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, task, priority FROM tasks WHERE deadline=? AND status='pending'",
        (today,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_all_pending():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, task, priority, category, deadline FROM tasks WHERE status='pending' ORDER BY deadline ASC"
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks
