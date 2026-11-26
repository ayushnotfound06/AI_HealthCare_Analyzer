"""
Generates synthetic training data for IntelliHealthcare:
  data/Disease_Symptoms.csv  -> symptom-based disease classifier
  data/heart.csv              -> heart disease risk classifier

The datasets are synthetic (rule-based + noise) since the original
project dataset was lost along with the code. Symptom profiles below
are written to reflect commonly documented signs of each condition.
"""
import random
import csv

random.seed(42)

SYMPTOMS = [
    "fever", "high_grade_fever", "cough", "fatigue", "headache", "chest_pain",
    "chest_tightness", "radiating_arm_pain", "dizziness", "sweating",
    "excess_sweating", "itching", "skin_rash", "hives", "skin_peeling",
    "swelling", "nausea", "vomiting", "diarrhea", "abdominal_pain",
    "abdominal_swelling", "runny_nose", "nasal_congestion", "sneezing",
    "sore_throat", "body_ache", "chills", "joint_pain", "muscle_weakness",
    "neck_pain", "stiff_neck", "blurred_vision", "sensitivity_to_light",
    "numbness", "one_sided_weakness", "slurred_speech", "confusion",
    "weight_loss", "loss_of_appetite", "yellowish_skin", "dark_urine",
    "blood_in_stool", "anal_pain", "anal_itching", "breathlessness",
    "shortness_of_breath", "palpitations", "high_blood_pressure",
    "mosquito_bite_history",
]

# disease -> {symptom: probability of being present}
DISEASE_PROFILES = {
    "Flu": {
        "fever": 0.9, "cough": 0.8, "fatigue": 0.8, "headache": 0.6,
        "body_ache": 0.8, "chills": 0.6, "sore_throat": 0.4,
    },
    "Common Cold": {
        "runny_nose": 0.9, "nasal_congestion": 0.8, "sneezing": 0.8,
        "sore_throat": 0.6, "cough": 0.5, "fatigue": 0.3, "fever": 0.2,
    },
    "Heart Attack": {
        "chest_pain": 0.95, "chest_tightness": 0.8, "radiating_arm_pain": 0.7,
        "sweating": 0.7, "excess_sweating": 0.6, "breathlessness": 0.7,
        "palpitations": 0.5, "dizziness": 0.4, "nausea": 0.4,
    },
    "Skin Allergy": {
        "itching": 0.9, "skin_rash": 0.85, "hives": 0.6, "swelling": 0.5,
        "skin_peeling": 0.3,
    },
    "Food Poisoning": {
        "nausea": 0.85, "vomiting": 0.8, "diarrhea": 0.85,
        "abdominal_pain": 0.8, "fever": 0.3, "fatigue": 0.4,
    },
    "Malaria": {
        "high_grade_fever": 0.9, "chills": 0.85, "sweating": 0.7,
        "headache": 0.6, "nausea": 0.4, "fatigue": 0.6,
        "mosquito_bite_history": 0.5,
    },
    "Dengue": {
        "high_grade_fever": 0.9, "headache": 0.7, "joint_pain": 0.8,
        "body_ache": 0.7, "skin_rash": 0.4, "fatigue": 0.5,
        "mosquito_bite_history": 0.5, "nausea": 0.3,
    },
    "Migraine": {
        "headache": 0.95, "sensitivity_to_light": 0.7, "nausea": 0.5,
        "blurred_vision": 0.4, "dizziness": 0.3, "vomiting": 0.2,
    },
    "Drug Reaction": {
        "skin_rash": 0.8, "itching": 0.7, "hives": 0.5, "swelling": 0.5,
        "fever": 0.3, "breathlessness": 0.2,
    },
    "Cervical Spondylosis": {
        "neck_pain": 0.9, "stiff_neck": 0.8, "muscle_weakness": 0.4,
        "numbness": 0.4, "headache": 0.3, "dizziness": 0.3,
    },
    "Alcoholic Hepatitis": {
        "yellowish_skin": 0.8, "abdominal_pain": 0.7, "abdominal_swelling": 0.5,
        "loss_of_appetite": 0.7, "fatigue": 0.6, "dark_urine": 0.5,
        "nausea": 0.4,
    },
    "Hypertension": {
        "high_blood_pressure": 0.95, "headache": 0.5, "dizziness": 0.5,
        "chest_pain": 0.2, "blurred_vision": 0.3, "palpitations": 0.3,
    },
    "Paralysis": {
        "one_sided_weakness": 0.85, "slurred_speech": 0.6, "confusion": 0.5,
        "numbness": 0.6, "blurred_vision": 0.3, "dizziness": 0.3,
    },
    "Pneumonia": {
        "fever": 0.8, "cough": 0.85, "breathlessness": 0.7,
        "chest_pain": 0.5, "fatigue": 0.6, "chills": 0.4,
    },
    "Dimorphic Hemorrhoids(piles)": {
        "blood_in_stool": 0.8, "anal_pain": 0.75, "anal_itching": 0.7,
        "swelling": 0.4, "abdominal_pain": 0.2,
    },
}

DISEASES = list(DISEASE_PROFILES.keys())
ROWS_PER_DISEASE = 26


def make_row(disease):
    profile = DISEASE_PROFILES[disease]
    row = {s: 0 for s in SYMPTOMS}
    for symptom, prob in profile.items():
        if random.random() < prob:
            row[symptom] = 1
    # ensure at least 2 symptoms present so the row is meaningful
    present = [s for s in profile if row[s] == 1]
    if len(present) < 2:
        for s in list(profile.keys())[:2]:
            row[s] = 1
    # small chance of an unrelated noise symptom (real-world messiness)
    if random.random() < 0.1:
        row[random.choice(SYMPTOMS)] = 1
    return row


def build_disease_csv(path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Disease"] + SYMPTOMS)
        for disease in DISEASES:
            for _ in range(ROWS_PER_DISEASE):
                row = make_row(disease)
                writer.writerow([disease] + [row[s] for s in SYMPTOMS])


def build_heart_csv(path, n=500):
    rows = []
    for _ in range(n):
        age = random.randint(29, 77)
        sex = random.choice([0, 1])
        cp = random.choice([0, 1, 2, 3])
        trestbps = random.randint(94, 200)
        chol = random.randint(126, 400)
        fbs = 1 if random.random() < 0.15 else 0
        restecg = random.choice([0, 1, 2])
        thalach = random.randint(71, 202)
        exang = 1 if random.random() < 0.3 else 0
        oldpeak = round(random.uniform(0, 6.2), 1)
        slope = random.choice([0, 1, 2])
        ca = random.choice([0, 1, 2, 3])
        thal = random.choice([0, 1, 2, 3])

        risk = 0
        risk += (age - 29) / 48
        risk += 0.4 if sex == 1 else 0
        risk += 0.5 if cp == 0 else -0.1
        risk += (trestbps - 94) / 106 * 0.6
        risk += (chol - 126) / 274 * 0.6
        risk += 0.3 if fbs else 0
        risk += (200 - thalach) / 131 * 0.7
        risk += 0.6 if exang else 0
        risk += oldpeak / 6.2 * 0.8
        risk += 0.4 if slope == 0 else 0
        risk += ca * 0.2
        risk += 0.3 if thal in (1, 3) else 0
        risk += random.uniform(-0.8, 0.8)  # noise

        target = 1 if risk > 2.3 else 0
        rows.append([age, sex, cp, trestbps, chol, fbs, restecg, thalach,
                     exang, oldpeak, slope, ca, thal, target])

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["age", "sex", "cp", "trestbps", "chol", "fbs",
                          "restecg", "thalach", "exang", "oldpeak", "slope",
                          "ca", "thal", "target"])
        writer.writerows(rows)


if __name__ == "__main__":
    build_disease_csv("data/Disease_Symptoms.csv")
    build_heart_csv("data/heart.csv")
    print("Generated data/Disease_Symptoms.csv and data/heart.csv")
