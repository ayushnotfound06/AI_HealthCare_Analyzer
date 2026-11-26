"""Trains the clinical-input heart disease risk classifier and pickles it
along with the scaler and feature order the Flask app needs at inference time.
"""
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_PATH = "data/heart.csv"
MODEL_PATH = "models/heart_model.pkl"

FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]


def main():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_train_scaled, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test_scaled))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "scaler": scaler,
            "features": FEATURES,
            "accuracy": accuracy,
        }, f)

    print(f"Heart model trained. Test accuracy: {accuracy * 100:.2f}%")


if __name__ == "__main__":
    main()
