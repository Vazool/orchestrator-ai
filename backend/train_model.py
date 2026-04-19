import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score,roc_curve,classification_report)
import seaborn as sns
import numpy as np 
import matplotlib.pyplot as plt


#Load data
df = pd.read_csv("historical_events.csv")
X = df[["severity", "event_type", "location_type", "days_before_travel", "policy_type"]]
y = df["disruption"]

#Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42, stratify=y)

#Build and train 
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["event_type", "location_type"])
    ],
    remainder="passthrough"
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(X_train, y_train)

#predictions
y_pred = model.predict(X_test)
y_pred_prob = model.predict_proba(X_test)[:,1]#for roc curve

#metrics
accuracy = accuracy_score(y_test,y_pred)
precision = precision_score(y_test,y_pred)
recall = recall_score(y_test,y_pred)
f1 = f1_score(y_test,y_pred)
roc_auc = roc_auc_score(y_test, y_pred_prob)
print("=" * 45)
print("        MODEL EVALUATION RESULTS")
print("=" * 45)
print(f"  Accuracy  : {accuracy:.2%}")
print(f"  Precision : {precision:.2%}")
print(f"  Recall    : {recall:.2%}  ← most important for us")
print(f"  F1 Score  : {f1:.2%}")
print(f"  ROC-AUC   : {roc_auc:.2%}")
print("=" * 45)
print("\nFull Classification Report:")
print(classification_report(y_test, y_pred))

#cross validation --model is stable
cv_scores = cross_val_score(model, X, y, cv=5, scoring="recall")
print(f"Cross-Val Recall (5-fold): {cv_scores.mean():.2%} ± {cv_scores.std():.2%}")



# Confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Create figure with 3 plots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- Plot 1: Confusion Matrix ---
sns.heatmap(
    cm, annot=True, fmt="d", cmap="Blues", ax=axes[0],
    xticklabels=["No Disruption", "Disruption"],
    yticklabels=["No Disruption", "Disruption"],
    linewidths=0.5, linecolor="white"
)
axes[0].set_title("Confusion Matrix", fontweight="bold")
axes[0].set_ylabel("Actual")
axes[0].set_xlabel("Predicted")
# Annotate what each quadrant means
tn, fp, fn, tp = cm.ravel()
axes[0].text(0.5, -0.18,
    f"TN={tn} (correct no-alert)   FP={fp} (unnecessary alert)\n"
    f"FN={fn} (missed traveller)   TP={tp} (correct alert)",
    transform=axes[0].transAxes, ha="center", fontsize=8, color="#555"
)

# --- Plot 2: Metrics Bar Chart ---
metrics = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
values  = [accuracy, precision, recall, f1, roc_auc]
colors  = ["#3b82f6", "#6366f1", "#ef4444", "#10b981", "#f59e0b"]

bars = axes[1].bar(metrics, values, color=colors, width=0.5, edgecolor="white", linewidth=1.2)
axes[1].set_ylim(0, 1.15)
axes[1].set_title("Key Metrics Overview", fontweight="bold")
axes[1].set_ylabel("Score")
axes[1].axhline(y=0.8, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
axes[1].text(4.6, 0.81, "0.80 target", fontsize=7, color="gray")

for bar, val in zip(bars, values):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{val:.0%}", ha="center", fontsize=9, fontweight="bold"
    )

# Highlight recall bar with a star
recall_idx = metrics.index("Recall")
axes[1].text(
    recall_idx, values[recall_idx] + 0.07,
    "★ key", ha="center", fontsize=8, color="#ef4444", fontweight="bold"
)

# --- Plot 3: ROC Curve ---
fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
axes[2].plot(fpr, tpr, color="#3b82f6", lw=2, label=f"ROC Curve (AUC = {roc_auc:.2f})")
axes[2].plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1, label="Random Guess")
axes[2].fill_between(fpr, tpr, alpha=0.08, color="#3b82f6")
axes[2].set_title("ROC Curve", fontweight="bold")
axes[2].set_xlabel("False Positive Rate")
axes[2].set_ylabel("True Positive Rate (Recall)")
axes[2].legend(loc="lower right", fontsize=9)
axes[2].set_xlim([0, 1])
axes[2].set_ylim([0, 1.05])

plt.tight_layout()
plt.savefig("model_evaluation.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n Saved: model_evaluation.png")

joblib.dump(model, "risk_model.pkl")

print("Retrained risk_model.pkl with variability.")
