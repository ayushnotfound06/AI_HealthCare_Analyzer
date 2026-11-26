"""Trains the symptom -> disease Decision Tree classifier and pickles it
along with the symptom/disease metadata the Flask app needs at inference time.
"""
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

DATA_PATH = "data/Disease_Symptoms.csv"
MODEL_PATH = "models/disease_model.pkl"


def main():
    df = pd.read_csv(DATA_PATH)
    symptoms = list(df.columns[1:])
    diseases = sorted(df["Disease"].unique())

    X = df[symptoms]
    y = df["Disease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = DecisionTreeClassifier(max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "symptoms": symptoms,
            "diseases": diseases,
            "accuracy": accuracy,
        }, f)

    print(f"Disease model trained. Test accuracy: {accuracy * 100:.2f}%")
    print(f"Symptoms: {len(symptoms)} | Diseases: {len(diseases)}")


if __name__ == "__main__":
    main()
