"""
Dataset Generator for Aria Academic Assistant
Combines:
  1. Expanded UCI Student Performance data (synthetic expansion of real data)
  2. Synthetic "Students Performance in Exams" style data (Kaggle-compatible)
Output: data/combined_dataset.csv  (5000+ rows)
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ── Part 1: Expand UCI Student Performance data ──────────────────────────────

def expand_uci(target_rows=3000):
    df_mat = pd.read_csv(os.path.join("data", "student-mat.csv"), sep=";")
    df_por = pd.read_csv(os.path.join("data", "student-por.csv"), sep=";")
    df_mat["subject"] = "math"
    df_por["subject"] = "portuguese"
    df = pd.concat([df_mat, df_por], ignore_index=True)

    rows_needed = target_rows - len(df)
    synthetic_rows = []

    for _ in range(rows_needed):
        base = df.sample(1).iloc[0].to_dict()
        # Add small noise to numeric columns
        for col in ["age", "studytime", "failures", "absences", "G1", "G2", "G3",
                    "famrel", "freetime", "goout", "Dalc", "Walc", "health",
                    "Medu", "Fedu", "traveltime"]:
            if col in base:
                noise = np.random.randint(-1, 2)
                base[col] = int(np.clip(base[col] + noise, 0, 20))
        synthetic_rows.append(base)

    df_synthetic = pd.DataFrame(synthetic_rows)
    df_expanded = pd.concat([df, df_synthetic], ignore_index=True)
    df_expanded["dataset_source"] = "UCI_Student_Performance"
    print(f"UCI expanded: {len(df_expanded)} rows, {len(df_expanded.columns)} columns")
    return df_expanded

# ── Part 2: Generate Kaggle-style "Students Performance in Exams" data ───────

def generate_exam_performance(n=2500):
    genders = ["male", "female"]
    races = ["group A", "group B", "group C", "group D", "group E"]
    parental_edu = ["some high school", "high school", "some college",
                    "associate's degree", "bachelor's degree", "master's degree"]
    lunch_types = ["standard", "free/reduced"]
    test_prep = ["none", "completed"]

    rows = []
    for _ in range(n):
        gender = np.random.choice(genders)
        race = np.random.choice(races)
        par_edu = np.random.choice(parental_edu)
        lunch = np.random.choice(lunch_types)
        prep = np.random.choice(test_prep)

        # Base score influenced by factors (realistic distribution)
        base = np.random.normal(65, 15)
        if lunch == "standard":
            base += 5
        if prep == "completed":
            base += 8
        if par_edu in ["bachelor's degree", "master's degree"]:
            base += 5
        if par_edu == "some high school":
            base -= 5

        math_score    = int(np.clip(base + np.random.normal(0, 8), 0, 100))
        reading_score = int(np.clip(base + np.random.normal(2, 7), 0, 100))
        writing_score = int(np.clip(base + np.random.normal(1, 7), 0, 100))
        avg_score     = round((math_score + reading_score + writing_score) / 3, 1)

        # Map to G3-style grade (0-20)
        g3_equiv = round(avg_score / 5, 1)

        # Derive studytime from scores
        studytime = 1
        if avg_score >= 70: studytime = 2
        if avg_score >= 80: studytime = 3
        if avg_score >= 90: studytime = 4

        rows.append({
            "gender": gender,
            "race_ethnicity": race,
            "parental_level_of_education": par_edu,
            "lunch": lunch,
            "test_preparation_course": prep,
            "math_score": math_score,
            "reading_score": reading_score,
            "writing_score": writing_score,
            "avg_score": avg_score,
            "G3": g3_equiv,
            "studytime": studytime,
            "failures": int(np.random.choice([0, 0, 0, 1, 2], p=[0.7, 0.1, 0.1, 0.07, 0.03])),
            "absences": int(np.clip(np.random.exponential(5), 0, 40)),
            "age": int(np.clip(np.random.normal(16, 1.5), 14, 22)),
            "subject": "general",
            "dataset_source": "Exam_Performance",
        })

    df = pd.DataFrame(rows)
    print(f"Exam Performance generated: {len(df)} rows, {len(df.columns)} columns")
    return df

# ── Part 3: Merge and save ────────────────────────────────────────────────────

def build_combined_dataset():
    print("Building combined dataset...")
    df_uci  = expand_uci(target_rows=3000)
    df_exam = generate_exam_performance(n=2500)

    # Align common columns for merge
    combined = pd.concat([df_uci, df_exam], ignore_index=True, sort=False)
    combined.fillna("unknown", inplace=True)

    out_path = os.path.join("data", "combined_dataset.csv")
    combined.to_csv(out_path, index=False)

    print(f"\nCombined dataset saved to: {out_path}")
    print(f"Total rows   : {len(combined)}")
    print(f"Total columns: {len(combined.columns)}")
    print(f"Total cells  : {combined.size}")
    print(f"Columns      : {list(combined.columns)}")
    return combined

if __name__ == "__main__":
    build_combined_dataset()
