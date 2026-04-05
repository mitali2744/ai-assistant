import os
import pandas as pd
import numpy as np
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore")

DATA_COMBINED = os.path.join("data", "combined_dataset.csv")
DATA_MAT      = os.path.join("data", "student-mat.csv")
DATA_POR      = os.path.join("data", "student-por.csv")

def _load_data():
    if os.path.exists(DATA_COMBINED):
        return pd.read_csv(DATA_COMBINED)
    df_mat = pd.read_csv(DATA_MAT, sep=";"); df_mat["subject"] = "math"
    df_por = pd.read_csv(DATA_POR, sep=";"); df_por["subject"] = "portuguese"
    return pd.concat([df_mat, df_por], ignore_index=True)

def _load_uci():
    df = _load_data()
    return df[df["dataset_source"] == "UCI_Student_Performance"] if "dataset_source" in df.columns else df

def _load_exam():
    df = _load_data()
    return df[df["dataset_source"] == "Exam_Performance"] if "dataset_source" in df.columns else pd.DataFrame()

def get_dataset_summary():
    df = _load_data()
    sources = df["dataset_source"].value_counts().to_dict() if "dataset_source" in df.columns else {}
    return (
        f"Combined dataset: {len(df)} rows, {len(df.columns)} columns, {df.size} total cells. "
        f"Sources: {sources}"
    )

def get_study_recommendation(studytime_hours_per_week=None, failures=0, absences=0):
    df = _load_uci().copy()
    df = df[pd.to_numeric(df["studytime"], errors="coerce").notna()]
    df["studytime"] = df["studytime"].astype(int)
    study_map = {1: 1, 2: 3.5, 3: 7.5, 4: 12, 5: 12}
    avg_by_study = df.groupby("studytime")["G3"].mean()
    avg_by_study = avg_by_study[avg_by_study.index.isin(study_map.keys())]

    if studytime_hours_per_week is not None:
        bucket = 1 if studytime_hours_per_week < 2 else 2 if studytime_hours_per_week < 5 else 3 if studytime_hours_per_week < 10 else 4
    else:
        bucket = 2

    user_avg   = avg_by_study.get(bucket, 10)
    best_avg   = avg_by_study.max()
    best_hours = study_map[avg_by_study.idxmax()]
    total      = len(_load_data())

    failure_advice = ""
    if failures > 0:
        hf = df[df["failures"] > 0]["G3"].mean()
        nf = df[df["failures"] == 0]["G3"].mean()
        failure_advice = f" Students with failures avg {hf:.1f} vs {nf:.1f} — extra revision recommended."

    absence_advice = " High absences correlate with lower grades — improve attendance." if absences > 10 else ""

    return (
        f"Based on {total} student records: studying ~{best_hours}h/week scores highest (avg {best_avg:.1f}/20). "
        f"Your level averages {user_avg:.1f}/20.{failure_advice}{absence_advice}"
    )

def predict_grade(studytime, failures, absences, goout=3, health=3):
    df = _load_uci().copy()
    features = ["studytime", "failures", "absences", "goout", "health"]
    df = df[features + ["G3"]].apply(pd.to_numeric, errors="coerce").dropna()
    model = LinearRegression()
    model.fit(df[features].values, df["G3"].values)
    pred = float(np.clip(model.predict([[studytime, failures, absences, goout, health]])[0], 0, 20))
    level = "Excellent" if pred >= 15 else "Good" if pred >= 12 else "Average" if pred >= 10 else "Needs Improvement"
    return f"Grade Prediction (UCI + Synthetic, {len(df)} records): ~{pred:.1f}/20 — {level}. Tip: reduce absences and increase study time."

def cluster_student_profile(studytime, failures, absences, goout):
    df = _load_uci().copy()
    features = ["studytime", "failures", "absences", "goout"]
    df = df[features].apply(pd.to_numeric, errors="coerce").dropna()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(df.values)
    cluster = kmeans.predict([[studytime, failures, absences, goout]])[0]
    order = np.argsort(kmeans.cluster_centers_[:, 0])[::-1]
    rank = list(order).index(cluster)
    profiles = ["High Achiever", "Average Student", "At-Risk Student"]
    tips = {
        "High Achiever": "You are in the top study group. Keep it up!",
        "Average Student": "Increasing study time by 1-2 hours/week could push you higher.",
        "At-Risk Student": "Try reducing goout time and focusing on consistent daily study."
    }
    profile = profiles[rank]
    return f"Student Profile (K-Means, {len(df)} records): {profile}. {tips[profile]}"

def get_exam_insights(gender=None, test_prep=None):
    df = _load_exam().copy()
    if df.empty:
        return "Exam performance data not available."
    for col in ["math_score", "reading_score", "writing_score", "avg_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["avg_score"])

    msg = f"Exam Performance Analysis ({len(df)} students): "
    msg += f"Avg math: {df['math_score'].mean():.1f}, reading: {df['reading_score'].mean():.1f}, writing: {df['writing_score'].mean():.1f}. "

    prep = df.groupby("test_preparation_course")["avg_score"].mean()
    if "completed" in prep and "none" in prep:
        msg += f"Test prep boosts avg score by {prep['completed'] - prep['none']:.1f} points. "

    if "parental_level_of_education" in df.columns:
        top_edu = df.groupby("parental_level_of_education")["avg_score"].mean().idxmax()
        msg += f"Students with '{top_edu}' parents score highest."

    return msg

def generate_synthetic_tasks():
    return [
        ("Complete assignment", "high", "general", 3),
        ("Study for exam", "high", "math", 5),
        ("Read textbook chapter", "medium", "science", 2),
        ("Submit project report", "high", "general", 4),
        ("Practice problems", "medium", "math", 2),
        ("Watch lecture recording", "low", "general", 1),
        ("Group study session", "medium", "general", 3),
        ("Revise notes", "medium", "general", 1.5),
        ("Lab report", "high", "science", 4),
        ("Prepare presentation", "high", "general", 5),
    ]

def show_dataset_insights():
    df = _load_data()
    df_uci  = _load_uci().copy()
    df_exam = _load_exam().copy()

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(f"Aria — Combined Dataset Insights ({len(df)} students, {len(df.columns)} features)",
                 fontsize=15, fontweight="bold")
    gs = gridspec.GridSpec(3, 3, figure=fig)

    # 1. Dataset source distribution
    ax1 = fig.add_subplot(gs[0, 0])
    if "dataset_source" in df.columns:
        src = df["dataset_source"].value_counts()
        ax1.bar(["UCI", "Exam"], src.values, color=["#3498db", "#e74c3c"], edgecolor="black")
        ax1.set_title("Students by Dataset Source")
        ax1.set_ylabel("Count")

    # 2. Grade (G3) distribution — UCI
    ax2 = fig.add_subplot(gs[0, 1])
    g3 = pd.to_numeric(df_uci["G3"], errors="coerce").dropna()
    ax2.hist(g3, bins=20, color="#2ecc71", edgecolor="black")
    ax2.set_title("Final Grade Distribution (UCI)")
    ax2.set_xlabel("Grade (0-20)")

    # 3. Study time vs avg grade
    ax3 = fig.add_subplot(gs[0, 2])
    study_map = {1: "<2h", 2: "2-5h", 3: "5-10h", 4: ">10h"}
    df_uci2 = df_uci.copy()
    df_uci2["studytime"] = pd.to_numeric(df_uci2["studytime"], errors="coerce")
    df_uci2["G3"] = pd.to_numeric(df_uci2["G3"], errors="coerce")
    avg_g = df_uci2.groupby("studytime")["G3"].mean()
    ax3.bar([study_map.get(k, str(k)) for k in avg_g.index], avg_g.values, color="#f39c12", edgecolor="black")
    ax3.set_title("Avg Grade by Study Time (UCI)")
    ax3.set_ylabel("Avg Grade")

    # 4. Exam scores distribution
    ax4 = fig.add_subplot(gs[1, 0])
    if not df_exam.empty:
        for col, color in [("math_score", "#e74c3c"), ("reading_score", "#3498db"), ("writing_score", "#2ecc71")]:
            scores = pd.to_numeric(df_exam[col], errors="coerce").dropna()
            ax4.hist(scores, bins=20, alpha=0.5, label=col.replace("_score", ""), color=color)
        ax4.set_title("Exam Score Distribution")
        ax4.set_xlabel("Score (0-100)")
        ax4.legend(fontsize=8)

    # 5. Test prep impact
    ax5 = fig.add_subplot(gs[1, 1])
    if not df_exam.empty and "test_preparation_course" in df_exam.columns:
        df_exam["avg_score"] = pd.to_numeric(df_exam["avg_score"], errors="coerce")
        prep_avg = df_exam.groupby("test_preparation_course")["avg_score"].mean()
        ax5.bar(prep_avg.index, prep_avg.values, color=["#e67e22", "#27ae60"], edgecolor="black")
        ax5.set_title("Test Prep vs Avg Score")
        ax5.set_ylabel("Avg Score")

    # 6. Parental education vs score
    ax6 = fig.add_subplot(gs[1, 2])
    if not df_exam.empty and "parental_level_of_education" in df_exam.columns:
        df_exam["avg_score"] = pd.to_numeric(df_exam["avg_score"], errors="coerce")
        edu_avg = df_exam.groupby("parental_level_of_education")["avg_score"].mean().sort_values()
        ax6.barh(edu_avg.index, edu_avg.values, color="#9b59b6", edgecolor="black")
        ax6.set_title("Parental Education vs Score")
        ax6.set_xlabel("Avg Score")
        ax6.tick_params(axis="y", labelsize=7)

    # 7. Failures vs grade
    ax7 = fig.add_subplot(gs[2, 0])
    df_uci2["failures"] = pd.to_numeric(df_uci2["failures"], errors="coerce")
    fail_avg = df_uci2.groupby("failures")["G3"].mean()
    ax7.bar(fail_avg.index.astype(str), fail_avg.values, color="#e74c3c", edgecolor="black")
    ax7.set_title("Failures vs Avg Grade (UCI)")
    ax7.set_xlabel("Past Failures")

    # 8. Absences vs grade scatter
    ax8 = fig.add_subplot(gs[2, 1])
    df_uci2["absences"] = pd.to_numeric(df_uci2["absences"], errors="coerce")
    ax8.scatter(df_uci2["absences"], df_uci2["G3"], alpha=0.2, color="#1abc9c", s=10)
    ax8.set_title("Absences vs Grade (UCI)")
    ax8.set_xlabel("Absences")
    ax8.set_ylabel("Grade")

    # 9. Gender vs exam score
    ax9 = fig.add_subplot(gs[2, 2])
    if not df_exam.empty and "gender" in df_exam.columns:
        gender_avg = df_exam.groupby("gender")["avg_score"].mean()
        ax9.bar(gender_avg.index, gender_avg.values, color=["#3498db", "#e91e8c"], edgecolor="black")
        ax9.set_title("Gender vs Avg Score")
        ax9.set_ylabel("Avg Score")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.savefig("dataset_insights.png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return f"IMAGE:{img_b64}"

def predict_pass_fail(studytime, failures, absences, goout=3, health=3):
    """SVM-based pass/fail classification (G3 >= 10 = pass)."""
    df = _load_uci().copy()
    features = ["studytime", "failures", "absences", "goout", "health"]
    df = df[features + ["G3"]].apply(pd.to_numeric, errors="coerce").dropna()

    X = df[features].values
    y = (df["G3"].values >= 10).astype(int)  # 1 = pass, 0 = fail

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = SVC(kernel="rbf", C=1.0, gamma="scale", random_state=42)
    model.fit(X_train_s, y_train)

    acc = accuracy_score(y_test, model.predict(X_test_s))

    user_input = scaler.transform([[studytime, failures, absences, goout, health]])
    prediction = model.predict(user_input)[0]
    confidence = model.decision_function(user_input)[0]

    result = "Pass ✅" if prediction == 1 else "Fail ❌"
    tip = (
        "Keep it up! Maintain your study habits." if prediction == 1
        else "At risk of failing. Try increasing study time and reducing absences."
    )

    return (
        f"SVM Pass/Fail Prediction (RBF kernel, {len(df)} records, accuracy: {acc*100:.1f}%): "
        f"{result}. {tip} "
        f"[studytime={studytime}, failures={failures}, absences={absences}]"
    )
