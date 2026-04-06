from database.db import get_connection              # SQLite connection
from datetime import datetime                       # for completion timestamps
from core.gamification import add_xp, update_streak # XP and streak rewards

def add_task(task, priority="medium", category="general", deadline=None, user_id=1):
    task = task.strip()   # remove leading/trailing spaces
    if not task:
        return "Please provide a task name."
    conn   = get_connection()
    cursor = conn.cursor()
    # insert task into DB with all fields
    cursor.execute(
        "INSERT INTO tasks (user_id, task, priority, category, deadline) VALUES (?, ?, ?, ?, ?)",
        (user_id, task, priority.lower(), category.lower(), deadline)
    )
    conn.commit()
    conn.close()
    # build confirmation message
    msg = f"Task '{task}' added with {priority} priority"
    if category != "general":
        msg += f" under {category}"   # mention category if not default
    if deadline:
        msg += f", due on {deadline}" # mention deadline if provided
    add_xp(5, "added a task")         # reward 5 XP for adding a task
    return msg + "."

def show_tasks(category=None, priority=None, user_id=1):
    conn   = get_connection()
    cursor = conn.cursor()
    # base SQL query — always filter by user_id
    query  = "SELECT id, task, status, priority, category, deadline FROM tasks WHERE user_id=?"
    params = [user_id]
    if category:                          # optional: filter by category
        query += " AND category=?"
        params.append(category.lower())
    if priority:                          # optional: filter by priority
        query += " AND priority=?"
        params.append(priority.lower())
    # sort: high=1, medium=2, low=3 — then newest first
    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC"
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    if not tasks:
        return "You have no tasks right now."
    lines = ["Your Tasks\n" + "-" * 40]
    for t in tasks:
        status_icon = "✅" if t[2] == "completed" else "⏳"              # status emoji
        pri_icon    = "🔴" if t[3] == "high" else "🟡" if t[3] == "medium" else "🟢"  # priority emoji
        line = f"{status_icon} {pri_icon} [{t[0]}] {t[1]}"
        if t[4] != "general":
            line += f"  |  {t[4]}"   # show category if not general
        if t[5]:
            line += f"  |  due: {t[5]}"  # show deadline if set
        lines.append(line)
    return "\n".join(lines)

def complete_task(task_id, user_id=1):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT priority FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return f"Task {task_id} not found."
    priority = row[0]   # get priority to calculate XP reward
    # mark task as completed and record the completion timestamp
    cursor.execute(
        "UPDATE tasks SET status='completed', completed_at=? WHERE id=? AND user_id=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id, user_id)
    )
    conn.commit()
    conn.close()
    xp_amount  = {"high": 30, "medium": 20, "low": 10}.get(priority, 20)  # XP by priority
    xp_msg     = add_xp(xp_amount, f"completed {priority} priority task")
    streak_msg = update_streak(priority=priority)
    msg = f"Task {task_id} marked as completed! Great work!"
    if streak_msg:
        msg += " " + streak_msg   # add streak/badge message if earned
    msg += " | " + xp_msg
    return msg

def delete_task(task_id, user_id=1):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
    conn.commit()
    conn.close()
    return f"Task {task_id} deleted."

def get_task_counts(user_id=1):
    # returns e.g. {"pending": 3, "completed": 5}
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM tasks WHERE user_id=? GROUP BY status", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}   # convert list of tuples to dict

def get_due_today(user_id=1):
    today  = datetime.now().strftime("%Y-%m-%d")   # today's date as string
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, task, priority FROM tasks WHERE deadline=? AND status='pending' AND user_id=?",
        (today, user_id)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_all_pending(user_id=1):
    conn   = get_connection()
    cursor = conn.cursor()
    # get all pending tasks sorted by deadline (earliest first, NULLs last)
    cursor.execute(
        "SELECT id, task, priority, category, deadline FROM tasks WHERE status='pending' AND user_id=? ORDER BY deadline ASC",
        (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks
