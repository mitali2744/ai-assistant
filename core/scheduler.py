from datetime import datetime, timedelta
from core.command_handler import get_all_pending

def check_deadlines():
    tasks = get_all_pending()
    today = datetime.now().date()
    urgent = []
    upcoming = []

    for t in tasks:
        if t[4]:
            try:
                due = datetime.strptime(t[4], "%Y-%m-%d").date()
                diff = (due - today).days
                if diff < 0:
                    urgent.append("OVERDUE: '" + t[1] + "' was due on " + t[4])
                elif diff == 0:
                    urgent.append("DUE TODAY: '" + t[1] + "'")
                elif diff <= 3:
                    upcoming.append("'" + t[1] + "' due in " + str(diff) + " day(s) on " + t[4])
            except ValueError:
                pass

    if not urgent and not upcoming:
        return "No urgent deadlines. You're on track!"

    msg = ""
    if urgent:
        msg += "URGENT: " + "; ".join(urgent) + ". "
    if upcoming:
        msg += "Upcoming: " + "; ".join(upcoming) + "."
    return msg.strip()

def generate_study_schedule():
    tasks = get_all_pending()
    today = datetime.now().date()

    if not tasks:
        return "No pending tasks to schedule."

    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks_with_deadline = []
    tasks_no_deadline = []

    for t in tasks:
        if t[4]:
            try:
                due = datetime.strptime(t[4], "%Y-%m-%d").date()
                tasks_with_deadline.append((t, due))
            except ValueError:
                tasks_no_deadline.append(t)
        else:
            tasks_no_deadline.append(t)

    tasks_with_deadline.sort(key=lambda x: (x[1], priority_order.get(x[0][2], 1)))
    tasks_no_deadline.sort(key=lambda x: priority_order.get(x[2], 1))

    current_day = today
    lines = ["Suggested Study Schedule", "-" * 40]

    for t, due in tasks_with_deadline:
        pri = t[2].upper()
        lines.append(current_day.strftime("%A %d %b") + "  [" + pri + "]  " + t[1] + "  (due " + t[4] + ")")
        current_day += timedelta(days=1)

    for t in tasks_no_deadline:
        pri = t[2].upper()
        lines.append(current_day.strftime("%A %d %b") + "  [" + pri + "]  " + t[1])
        current_day += timedelta(days=1)

    return "\n".join(lines)

def predict_completion():
    from database.db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT created_at, completed_at FROM tasks WHERE status='completed' AND completed_at IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return "Not enough data yet to predict completion time. Complete more tasks first."

    durations = []
    for created, completed in rows:
        try:
            c = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
            d = datetime.strptime(completed, "%Y-%m-%d %H:%M:%S")
            durations.append((d - c).total_seconds() / 3600)
        except Exception:
            pass

    if not durations:
        return "Could not calculate prediction from existing data."

    avg_hours = sum(durations) / len(durations)
    pending = get_all_pending()
    if not pending:
        return "No pending tasks to predict."

    total_predicted = avg_hours * len(pending)
    days = total_predicted / 8

    return (
        "Based on your history, you complete tasks in ~" + str(round(avg_hours, 1)) + " hours on average. "
        "With " + str(len(pending)) + " pending tasks, estimated completion: "
        + str(round(total_predicted, 1)) + " hours (~" + str(round(days, 1)) + " study days)."
    )
