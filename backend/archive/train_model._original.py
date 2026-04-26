import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

df = pd.read_csv("historical_events.csv")

X = df[["severity", "event_type", "location_type", "days_before_travel", "policy_type"]]
y = df["disruption"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["event_type", "location_type"])
    ],
    remainder="passthrough"
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=500))
])

model.fit(X, y)
joblib.dump(model, "risk_model.pkl")

print("Retrained risk_model.pkl with variability.")
