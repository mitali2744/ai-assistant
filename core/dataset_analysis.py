# ── Imports ──────────────────────────────────────────────────────────────────
import os
import pandas as pd
import numpy as np
import io
import base64
import matplotlib
matplotlib.use("Agg")            # non-interactive backend (no popup window)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LinearRegression  # supervised regression
from sklearn.cluster import KMeans                 # unsupervised clustering
from sklearn.svm import SVC                        # classification model
from sklearn.preprocessing import StandardScaler  # normalize features for SVM
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore")

# ── Dataset paths ─────────────────────────────────────────────────────────────
DATA_COMBINED = os.path.join("data", "combined_dataset.csv")
DATA_MAT      = os.path.join("data", "student-mat.csv")
DATA_POR      = os.path.join("data", "student-por.csv")

def _load_data():
    # use pre-merged file if available, else merge UCI CSVs manually
    if os.path.exists(DATA_COMBINED):
        return pd.read_csv(DATA_COMBINED)
    df_mat = pd.read_csv(DATA_MAT, sep=";"); df_mat["subject"] = "math"
    df_por = pd.read_csv(DATA_POR, sep=";"); df_por["subject"] = "portuguese"
    return pd.concat([df_mat, df_por], ignore_index=True)

def _load_uci():
    # filter only UCI Student Performance rows
    df = _load_data()
    return df[df["dataset_source"] == "UCI_Student_Performance"] if "dataset_source" in df.columns else df

def _load_exam():
    # filter only Exam Performance rows (math/reading/writing scores)
    df = _load_data()
    return df[df["dataset_source"] == "Exam_Performance"] if "dataset_source" in df.columns else pd.DataFrame()

def get_dataset_summary():
    # return total rows, columns, and source breakdown
    df = _load_data()
    sources = df["dataset_source"].value_counts().to_dict() if "dataset_source" in df.columns else {}
    return (
        f"Combined dataset: {len(df)} rows, {len(df.columns)} columns, {df.size} total cells. "
        f"Sources: {sources}"
    )

def get_study_recommendation(studytime_hours_per_week=None, failures=0, absences=0):
    # give advice based on real student data averages
    df = _load_uci().copy()
    df = df[pd.to_numeric(df["studytime"], errors="coerce").notna()]
    df["studytime"] = df["studytime"].astype(int)

    # UCI scale: 1=<2h, 2=2-5h, 3=5-10h, 4=>10h
    study_map = {1: 1, 2: 3.5, 3: 7.5, 4: 12, 5: 12}
    avg_by_study = df.groupby("studytime")["G3"].mean()
    avg_by_study = avg_by_study[avg_by_study.index.isin(study_map.keys())]

    # convert user hours to UCI bucket
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
    # Linear Regression: G3 = b0 + b1*studytime + b2*failures + b3*absences + b4*goout + b5*health
    df = _load_uci().copy()
    features = ["studytime", "failures", "absences", "goout", "health"]
    df = df[features + ["G3"]].apply(pd.to_numeric, errors="coerce").dropna()
    model = LinearRegression()
    model.fit(df[features].values, df["G3"].values)  # train on UCI data
    pred = float(np.clip(model.predict([[studytime, failures, absences, goout, health]])[0], 0, 20))  # clip to 0-20
    level = "Excellent" if pred >= 15 else "Good" if pred >= 12 else "Average" if pred >= 10 else "Needs Improvement"
    return f"Grade Prediction (UCI + Synthetic, {len(df)} records): ~{pred:.1f}/20 — {level}. Tip: reduce absences and increase study time."

def cluster_student_profile(studytime, failures, absences, goout):
    # K-Means clustering: group students into 3 profiles based on study habits
    df = _load_uci().copy()
    features = ["studytime", "failures", "absences", "goout"]
    df = df[features].apply(pd.to_numeric, errors="coerce").dropna()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)  # 3 clusters, fixed seed
    kmeans.fit(df.values)
    cluster = kmeans.predict([[studytime, failures, absences, goout]])[0]  # user's cluster
    # sort clusters by studytime descending to rank best→worst
    order = np.argsort(kmeans.cluster_centers_[:, 0])[::-1]
    rank = list(order).index(cluster)  # 0=High Achiever, 1=Average, 2=At-Risk
    profiles = ["High Achiever", "Average Student", "At-Risk Student"]
    tips = {
        "High Achiever": "You are in the top study group. Keep it up!",
        "Average Student": "Increasing study time by 1-2 hours/week could push you higher.",
        "At-Risk Student": "Try reducing goout time and focusing on consistent daily study."
    }
    profile = profiles[rank]
    return f"Student Profile (K-Means, {len(df)} records): {profile}. {tips[profile]}"

def get_exam_insights(gender=None, test_prep=None):
    # analyze exam performance dataset for scores, test prep, parental education
    df = _load_exam().copy()
    if df.empty:
        return "Exam performance data not available."
    for col in ["math_score", "reading_score", "writing_score", "avg_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["avg_score"])

    msg = f"Exam Performance Analysis ({len(df)} students): "
    msg += f"Avg math: {df['math_score'].mean():.1f}, reading: {df['reading_score'].mean():.1f}, writing: {df['writing_score'].mean():.1f}. "

    # compare scores: students who completed test prep vs those who didn't
    prep = df.groupby("test_preparation_course")["avg_score"].mean()
    if "completed" in prep and "none" in prep:
        msg += f"Test prep boosts avg score by {prep['completed'] - prep['none']:.1f} points. "

    # find which parental education level gives highest avg score
    if "parental_level_of_education" in df.columns:
        top_edu = df.groupby("parental_level_of_education")["avg_score"].mean().idxmax()
        msg += f"Students with '{top_edu}' parents score highest."

    return msg

def generate_synthetic_tasks():
    # sample tasks used for demo/testing
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
