import io
import base64
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for web
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime
from database.db import get_connection

def analyze_productivity():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No task data available for productivity analysis."

    data = {row[0]: row[1] for row in rows}
    total = sum(data.values())
    completed = data.get("completed", 0)
    pending = data.get("pending", 0)
    score = (completed / total) * 100 if total > 0 else 0

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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    status_rows = cursor.fetchall()

    cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
    priority_rows = cursor.fetchall()

    cursor.execute("SELECT category, COUNT(*) FROM tasks GROUP BY category")
    category_rows = cursor.fetchall()

    cursor.execute(
        "SELECT DATE(created_at), COUNT(*) FROM tasks GROUP BY DATE(created_at) ORDER BY DATE(created_at)"
    )
    trend_rows = cursor.fetchall()

    conn.close()

    if not status_rows:
        return "No task data available to generate graph."

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("Aria - Academic Productivity Dashboard", fontsize=16, fontweight="bold")
    gs = gridspec.GridSpec(2, 3, figure=fig)

    # 1. Status bar chart
    ax1 = fig.add_subplot(gs[0, 0])
    labels = [r[0].capitalize() for r in status_rows]
    values = [r[1] for r in status_rows]
    colors = ["#4CAF50" if l == "Completed" else "#FF9800" for l in labels]
    ax1.bar(labels, values, color=colors, edgecolor="black")
    ax1.set_title("Task Status")
    ax1.set_ylabel("Count")
    for i, v in enumerate(values):
        ax1.text(i, v + 0.05, str(v), ha="center", fontweight="bold")

    # 2. Status pie chart
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
    ax2.set_title("Task Distribution")

    # 3. Priority breakdown
    ax3 = fig.add_subplot(gs[0, 2])
    if priority_rows:
        p_labels = [r[0].capitalize() for r in priority_rows]
        p_values = [r[1] for r in priority_rows]
        p_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}
        p_clrs = [p_colors.get(l, "#95a5a6") for l in p_labels]
        ax3.bar(p_labels, p_values, color=p_clrs, edgecolor="black")
        ax3.set_title("Tasks by Priority")
        ax3.set_ylabel("Count")

    # 4. Category breakdown
    ax4 = fig.add_subplot(gs[1, 0])
    if category_rows:
        c_labels = [r[0].capitalize() for r in category_rows]
        c_values = [r[1] for r in category_rows]
        ax4.barh(c_labels, c_values, color="#3498db", edgecolor="black")
        ax4.set_title("Tasks by Category")
        ax4.set_xlabel("Count")

    # 5. Task creation trend
    ax5 = fig.add_subplot(gs[1, 1:])
    if trend_rows:
        dates = [r[0] for r in trend_rows]
        counts = [r[1] for r in trend_rows]
        ax5.plot(dates, counts, marker="o", color="#9b59b6", linewidth=2)
        ax5.fill_between(dates, counts, alpha=0.2, color="#9b59b6")
        ax5.set_title("Task Creation Trend")
        ax5.set_ylabel("Tasks Added")
        ax5.tick_params(axis="x", rotation=45)

    plt.tight_layout()

    # Save to file for terminal mode
    plt.savefig("productivity_report.png", bbox_inches="tight")

    # Also return as base64 for web mode
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return f"IMAGE:{img_b64}"
