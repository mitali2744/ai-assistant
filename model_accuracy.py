"""
Run: python model_accuracy.py
Saves 6 separate PNG files and shows each as a popup.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, confusion_matrix

df  = pd.read_csv("data/combined_dataset.csv")
uci = df[df["dataset_source"] == "UCI_Student_Performance"].copy()
features = ["studytime", "failures", "absences", "goout", "health"]
uci = uci[features + ["G3"]].apply(pd.to_numeric, errors="coerce").dropna()
X, y = uci[features].values, uci["G3"].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

lr = LinearRegression()
lr.fit(X_tr, y_tr)
y_pred = lr.predict(X_te)
r2   = r2_score(y_te, y_pred)
rmse = np.sqrt(mean_squared_error(y_te, y_pred))

y_cls = (y >= 10).astype(int)
X_tr2, X_te2, y_tr2, y_te2 = train_test_split(X, y_cls, test_size=0.2, random_state=42)
sc  = StandardScaler()
svm = SVC(kernel="rbf", C=1.0, gamma="scale", random_state=42)
svm.fit(sc.fit_transform(X_tr2), y_tr2)
y_pred2 = svm.predict(sc.transform(X_te2))
acc = accuracy_score(y_te2, y_pred2)
cm  = confusion_matrix(y_te2, y_pred2)

inertias = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).inertia_ for k in range(1, 8)]

def save_show(fig, name):
    plt.tight_layout()
    fig.savefig(name, dpi=150)
    print(f"Saved: {name}")
    plt.show()

# Graph 1
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(y_te, y_pred, alpha=0.4, color="#3498db", s=20)
ax.plot([0,20],[0,20],"r--",linewidth=1.5,label="Perfect fit")
ax.set_title(f"Linear Regression — Actual vs Predicted\nR²={r2:.3f}  RMSE={rmse:.2f}")
ax.set_xlabel("Actual Grade"); ax.set_ylabel("Predicted Grade"); ax.legend()
save_show(fig, "graph1_lr_actual_vs_predicted.png")

# Graph 2
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(y_pred, y_te - y_pred, alpha=0.4, color="#e74c3c", s=20)
ax.axhline(0, color="black", linewidth=1.5, linestyle="--")
ax.set_title("Linear Regression — Residual Plot\n(closer to 0 = better)")
ax.set_xlabel("Predicted Grade"); ax.set_ylabel("Residual")
save_show(fig, "graph2_lr_residuals.png")

# Graph 3
fig, ax = plt.subplots(figsize=(7, 5))
colors = ["#2ecc71" if c > 0 else "#e74c3c" for c in lr.coef_]
ax.barh(features, lr.coef_, color=colors, edgecolor="black")
ax.axvline(0, color="black", linewidth=1)
ax.set_title("Linear Regression — Feature Coefficients\n(green=positive, red=negative impact)")
ax.set_xlabel("Coefficient Value")
save_show(fig, "graph3_lr_coefficients.png")

# Graph 4
fig, ax = plt.subplots(figsize=(6, 5))
ax.imshow(cm, cmap="Blues")
ax.set_title(f"SVM — Confusion Matrix\nAccuracy: {acc*100:.2f}%")
ax.set_xticks([0,1]); ax.set_yticks([0,1])
ax.set_xticklabels(["Fail","Pass"]); ax.set_yticklabels(["Fail","Pass"])
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i,j]), ha="center", va="center", fontsize=16,
                fontweight="bold", color="white" if cm[i,j]>200 else "black")
save_show(fig, "graph4_svm_confusion_matrix.png")

# Graph 5
fig, ax = plt.subplots(figsize=(6, 5))
fail_acc = cm[0,0]/(cm[0,0]+cm[0,1])*100
pass_acc = cm[1,1]/(cm[1,0]+cm[1,1])*100
ax.bar(["Fail","Pass"],[fail_acc,pass_acc],color=["#e74c3c","#2ecc71"],edgecolor="black")
ax.set_title(f"SVM — Per-Class Accuracy\nOverall: {acc*100:.2f}%")
ax.set_ylabel("Accuracy %"); ax.set_ylim(0, 115)
for i, v in enumerate([fail_acc, pass_acc]):
    ax.text(i, v+2, f"{v:.1f}%", ha="center", fontweight="bold", fontsize=12)
save_show(fig, "graph5_svm_class_accuracy.png")

# Graph 6
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(range(1,8), inertias, marker="o", color="#9b59b6", linewidth=2)
ax.axvline(3, color="red", linestyle="--", label="k=3 chosen")
ax.set_title("K-Means — Elbow Curve\n(optimal k=3)")
ax.set_xlabel("Number of Clusters (k)"); ax.set_ylabel("Inertia"); ax.legend()
save_show(fig, "graph6_kmeans_elbow.png")

print("\nAll 6 graphs saved.")
