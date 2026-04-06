from datetime import datetime, timedelta        # datetime for parsing dates, timedelta for adding days
from core.command_handler import get_all_pending  # fetch all pending tasks from DB

def check_deadlines():
    tasks = get_all_pending()          # get all pending tasks from database
    today = datetime.now().date()      # today's date (no time component)
    urgent   = []                      # tasks that are overdue or due today
    upcoming = []                      # tasks due within 3 days

    for t in tasks:
        if t[4]:                       # t[4] is the deadline field
            try:
                due  = datetime.strptime(t[4], "%Y-%m-%d").date()  # parse deadline string to date
                diff = (due - today).days                           # days until deadline (negative = overdue)
                if diff < 0:
                    urgent.append("OVERDUE: '" + t[1] + "' was due on " + t[4])   # past deadline
                elif diff == 0:
                    urgent.append("DUE TODAY: '" + t[1] + "'")                    # due today
                elif diff <= 3:
                    upcoming.append("'" + t[1] + "' due in " + str(diff) + " day(s) on " + t[4])  # due soon
            except ValueError:
                pass   # skip tasks with invalid date format

    if not urgent and not upcoming:
        return "No urgent deadlines. You're on track!"

    # build response message
    msg = ""
    if urgent:
        msg += "URGENT: " + "; ".join(urgent) + ". "
    if upcoming:
        msg += "Upcoming: " + "; ".join(upcoming) + "."
    return msg.strip()

def generate_study_schedule():
    tasks = get_all_pending()          # get all pending tasks
    today = datetime.now().date()      # start scheduling from today

    if not tasks:
        return "No pending tasks to schedule."

    # numeric sort order for priority (lower = higher priority)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks_with_deadline = []    # tasks that have a deadline
    tasks_no_deadline   = []    # tasks without a deadline

    for t in tasks:
        if t[4]:   # if deadline exists
            try:
                due = datetime.strptime(t[4], "%Y-%m-%d").date()
                tasks_with_deadline.append((t, due))   # store task with its parsed date
            except ValueError:
                tasks_no_deadline.append(t)   # invalid date — treat as no deadline
        else:
            tasks_no_deadline.append(t)

    # sort deadline tasks by date first, then by priority
    tasks_with_deadline.sort(key=lambda x: (x[1], priority_order.get(x[0][2], 1)))
    # sort no-deadline tasks by priority only
    tasks_no_deadline.sort(key=lambda x: priority_order.get(x[2], 1))

    current_day = today
    lines = ["Suggested Study Schedule", "-" * 40]

    # assign one task per day for deadline tasks
    for t, due in tasks_with_deadline:
        pri = t[2].upper()
        lines.append(current_day.strftime("%A %d %b") + "  [" + pri + "]  " + t[1] + "  (due " + t[4] + ")")
        current_day += timedelta(days=1)   # move to next day

    # assign remaining tasks after deadline tasks
    for t in tasks_no_deadline:
        pri = t[2].upper()
        lines.append(current_day.strftime("%A %d %b") + "  [" + pri + "]  " + t[1])
        current_day += timedelta(days=1)

    return "\n".join(lines)

def predict_completion():
    from database.db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    # fetch completed tasks that have both created_at and completed_at timestamps
    cursor.execute("SELECT created_at, completed_at FROM tasks WHERE status='completed' AND completed_at IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return "Not enough data yet to predict completion time. Complete more tasks first."

    durations = []
    for created, completed in rows:
        try:
            c = datetime.strptime(created,   "%Y-%m-%d %H:%M:%S")   # parse created time
            d = datetime.strptime(completed, "%Y-%m-%d %H:%M:%S")   # parse completed time
            durations.append((d - c).total_seconds() / 3600)        # convert seconds to hours
        except Exception:
            pass   # skip rows with bad timestamps

    if not durations:
        return "Could not calculate prediction from existing data."

    avg_hours = sum(durations) / len(durations)   # average hours per task
    pending   = get_all_pending()                 # get current pending tasks
    if not pending:
        return "No pending tasks to predict."

    total_predicted = avg_hours * len(pending)    # total hours = avg * number of tasks
    days = total_predicted / 8                    # assume 8 study hours per day

    return (
        "Based on your history, you complete tasks in ~" + str(round(avg_hours, 1)) + " hours on average. "
        "With " + str(len(pending)) + " pending tasks, estimated completion: "
        + str(round(total_predicted, 1)) + " hours (~" + str(round(days, 1)) + " study days)."
    )
