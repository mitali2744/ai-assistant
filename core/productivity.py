import io                   # in-memory buffer for saving image
import base64              # encode image as base64 string for browser
import matplotlib
matplotlib.use("Agg")      # non-interactive backend — no popup window
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec   # multi-panel layout
from datetime import datetime
from database.db import get_connection   # SQLite connection

def analyze_productivity():
    # calculate productivity score based on completed vs total tasks
    conn = get_connection()
    cursor = conn.cursor()
    # count tasks grouped by status (pending / completed)
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No task data available for productivity analysis."

    data = {row[0]: row[1] for row in rows}   # e.g. {"pending": 3, "completed": 7}
    total     = sum(data.values())             # total tasks
    completed = data.get("completed", 0)       # number completed
    pending   = data.get("pending", 0)         # number still pending
    score     = (completed / total) * 100 if total > 0 else 0  # completion %

    # classify productivity level based on score
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return (
        f"Productivity Analysis: {completed} completed, {pending} pending out of {total} tasks. "
        f"Score: {score:.1f}%. Productivity Level: {level}."
    )

def show_productivity_graph():
    # generate a 5-panel dashboard graph of task data and return as base64 image
    conn = get_connection()
    cursor = conn.cursor()

    # query 1: count tasks by status (pending/completed)
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    status_rows = cursor.fetchall()

    # query 2: count tasks by priority (high/medium/low)
    cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    priority_rows = cursor.fetchall()

    # query 3: count tasks by category (math/science/general etc.)
    cursor.execute("SELECT category, COUNT(*) FROM tasks GROUP BY category")
    category_rows = cursor.fetchall()

    # query 4: count tasks added per day (for trend line)
    cursor.execute(
        "SELECT DATE(created_at), COUNT(*) FROM tasks GROUP BY DATE(created_at) ORDER BY DATE(created_at)"
    )
    trend_rows = cursor.fetchall()
    conn.close()

    if not status_rows:
        return "No task data available to generate graph."

    # create figure: 16x10 inches, 2 rows x 3 columns grid
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("Aria - Academic Productivity Dashboard", fontsize=16, fontweight="bold")
    gs = gridspec.GridSpec(2, 3, figure=fig)

    # Panel 1 (top-left): bar chart of task status counts
    ax1 = fig.add_subplot(gs[0, 0])
    labels = [r[0].capitalize() for r in status_rows]   # e.g. ["Pending", "Completed"]
    values = [r[1] for r in status_rows]                 # e.g. [3, 7]
    colors = ["#4CAF50" if l == "Completed" else "#FF9800" for l in labels]  # green/orange
    ax1.bar(labels, values, color=colors, edgecolor="black")
    ax1.set_title("Task Status")
    ax1.set_ylabel("Count")
    for i, v in enumerate(values):
        ax1.text(i, v + 0.05, str(v), ha="center", fontweight="bold")  # label on top of bar

    # Panel 2 (top-middle): pie chart showing % completed vs pending
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
    ax2.set_title("Task Distribution")

    # Panel 3 (top-right): bar chart of tasks by priority
    ax3 = fig.add_subplot(gs[0, 2])
    if priority_rows:
        p_labels = [r[0].capitalize() for r in priority_rows]
        p_values = [r[1] for r in priority_rows]
        p_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}  # red/orange/green
        p_clrs = [p_colors.get(l, "#95a5a6") for l in p_labels]
        ax3.bar(p_labels, p_values, color=p_clrs, edgecolor="black")
        ax3.set_title("Tasks by Priority")
        ax3.set_ylabel("Count")

    # Panel 4 (bottom-left): horizontal bar chart of tasks by category
    ax4 = fig.add_subplot(gs[1, 0])
    if category_rows:
        c_labels = [r[0].capitalize() for r in category_rows]
        c_values = [r[1] for r in category_rows]
        ax4.barh(c_labels, c_values, color="#3498db", edgecolor="black")
        ax4.set_title("Tasks by Category")
        ax4.set_xlabel("Count")

    # Panel 5 (bottom-middle + right): line chart of tasks added per day
    ax5 = fig.add_subplot(gs[1, 1:])   # spans 2 columns
    if trend_rows:
        dates  = [r[0] for r in trend_rows]   # list of date strings
        counts = [r[1] for r in trend_rows]   # tasks added on each date
        ax5.plot(dates, counts, marker="o", color="#9b59b6", linewidth=2)
        ax5.fill_between(dates, counts, alpha=0.2, color="#9b59b6")  # shaded area under line
        ax5.set_title("Task Creation Trend")
        ax5.set_ylabel("Tasks Added")
        ax5.tick_params(axis="x", rotation=45)   # rotate x-axis dates for readability

    plt.tight_layout()   # auto-adjust spacing between panels

    plt.savefig("productivity_report.png", bbox_inches="tight")   # save to disk

    # also encode as base64 to send to browser without saving a file
    buf = io.BytesIO()                                             # in-memory buffer
    plt.savefig(buf, format="png", bbox_inches="tight")           # write PNG to buffer
    buf.seek(0)                                                    # rewind buffer to start
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")         # encode to base64 string
    plt.close()                                                    # free memory
    return f"IMAGE:{img_b64}"   # prefix tells frontend to render as image
