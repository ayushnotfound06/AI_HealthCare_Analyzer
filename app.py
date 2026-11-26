import os
import pickle
import urllib.request
import json as json_lib

import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

with open(os.path.join(MODELS_DIR, "disease_model.pkl"), "rb") as f:
    DISEASE_BUNDLE = pickle.load(f)

with open(os.path.join(MODELS_DIR, "heart_model.pkl"), "rb") as f:
    HEART_BUNDLE = pickle.load(f)

SYMPTOMS = DISEASE_BUNDLE["symptoms"]
DISEASES = DISEASE_BUNDLE["diseases"]
DISEASE_MODEL = DISEASE_BUNDLE["model"]
DISEASE_ACCURACY = DISEASE_BUNDLE["accuracy"]

HEART_MODEL = HEART_BUNDLE["model"]
HEART_SCALER = HEART_BUNDLE["scaler"]
HEART_FEATURES = HEART_BUNDLE["features"]
HEART_ACCURACY = HEART_BUNDLE["accuracy"]

# Short guidance shown alongside each predicted disease.
DISEASE_INFO = {
    "Flu": ("Common viral infection causing fever and body aches.",
            "Rest, fluids, and paracetamol usually help. See a doctor if fever lasts over 3 days.", "self-care"),
    "Common Cold": ("Mild viral infection of the nose and throat.",
                     "Rest and warm fluids are usually enough; recovery in a few days is normal.", "self-care"),
    "Heart Attack": ("Blockage of blood flow to the heart muscle.",
                      "This is a medical emergency. Call emergency services immediately.", "emergency"),
    "Skin Allergy": ("Immune reaction to an allergen causing skin irritation.",
                      "Avoid the suspected trigger and consider an antihistamine; see a doctor if it spreads.", "see-doctor"),
    "Food Poisoning": ("Illness caused by contaminated food or water.",
                        "Stay hydrated with oral rehydration salts; seek care if vomiting or diarrhea is severe.", "see-doctor"),
    "Malaria": ("Mosquito-borne parasitic infection.",
                "Needs a blood test and antimalarial treatment from a doctor promptly.", "see-doctor"),
    "Dengue": ("Mosquito-borne viral infection.",
               "Monitor for warning signs (bleeding, severe pain) and get a platelet count checked.", "see-doctor"),
    "Migraine": ("Recurring headache disorder, often with light sensitivity.",
                 "Rest in a dark quiet room; consult a doctor if headaches are frequent or severe.", "self-care"),
    "Drug Reaction": ("Adverse reaction to a medication.",
                       "Stop the suspected medicine and consult a doctor, especially if breathing is affected.", "see-doctor"),
    "Cervical Spondylosis": ("Age-related wear of neck spinal discs.",
                              "Physiotherapy and posture correction help; see a doctor for persistent numbness.", "see-doctor"),
    "Alcoholic Hepatitis": ("Liver inflammation caused by alcohol use.",
                             "Requires medical evaluation and abstinence from alcohol.", "see-doctor"),
    "Hypertension": ("Persistently high blood pressure.",
                      "Reduce salt intake and monitor blood pressure regularly; see a doctor for medication.", "see-doctor"),
    "Paralysis": ("Sudden loss of muscle function, often stroke-related.",
                  "This is a medical emergency. Seek immediate medical attention.", "emergency"),
    "Pneumonia": ("Infection causing inflammation in the lungs.",
                   "Needs medical evaluation; antibiotics or supportive care may be required.", "see-doctor"),
    "Dimorphic Hemorrhoids(piles)": ("Swollen veins in the lower rectum/anus.",
                                       "Increase fiber and fluids; consult a doctor if bleeding persists.", "self-care"),
}

DISEASE_LIST_DISPLAY = [
    "Malaria", "Hypertension", "Paralysis", "Pneumonia", "Dengue", "Migraine",
    "Drug Reaction", "Dimorphic Hemorrhoids(piles)", "Heart Attack",
    "Cervical Spondylosis", "Alcoholic Hepatitis", "Flu", "Common Cold",
    "Skin Allergy", "Food Poisoning",
]


def humanize(symptom_key):
    return symptom_key.replace("_", " ").title()


@app.route("/")
def root():
    return render_template("home.html", active="home")


@app.route("/home")
def home():
    return render_template("home.html", active="home")


@app.route("/disease-detector")
def disease_detector():
    symptom_options = sorted(SYMPTOMS, key=humanize)
    return render_template(
        "disease_detector.html",
        active="detector",
        symptoms=symptom_options,
        humanize=humanize,
    )


@app.route("/stats")
def stats():
    return render_template(
        "stats.html",
        active="stats",
        disease_accuracy=round(DISEASE_ACCURACY * 100, 1),
        heart_accuracy=round(HEART_ACCURACY * 100, 1),
        num_diseases=len(DISEASES),
        num_symptoms=len(SYMPTOMS),
    )


@app.route("/about")
def about():
    return render_template("about.html", active="about", diseases=DISEASE_LIST_DISPLAY)


@app.route("/predict-symptoms", methods=["POST"])
def predict_symptoms():
    payload = request.get_json(silent=True) or {}
    selected = set(payload.get("symptoms", []))

    if not selected:
        return jsonify({"error": "Please select at least one symptom."}), 400

    input_vector = pd.DataFrame([[1 if s in selected else 0 for s in SYMPTOMS]], columns=SYMPTOMS)
    prediction = DISEASE_MODEL.predict(input_vector)[0]

    confidence = None
    if hasattr(DISEASE_MODEL, "predict_proba"):
        proba = DISEASE_MODEL.predict_proba(input_vector)[0]
        confidence = round(float(max(proba)) * 100, 1)

    description, advice, urgency = DISEASE_INFO.get(
        prediction, ("", "Please consult a healthcare professional.", "see-doctor")
    )

    return jsonify({
        "disease": prediction,
        "description": description,
        "advice": advice,
        "urgency": urgency,
        "confidence": confidence,
    })


@app.route("/predict-heart", methods=["POST"])
def predict_heart():
    payload = request.get_json(silent=True) or {}
    try:
        input_vector = pd.DataFrame(
            [[float(payload[f]) for f in HEART_FEATURES]], columns=HEART_FEATURES
        )
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Please fill in all fields with valid numbers."}), 400

    scaled = HEART_SCALER.transform(input_vector)
    prediction = int(HEART_MODEL.predict(scaled)[0])
    proba = HEART_MODEL.predict_proba(scaled)[0]
    risk_probability = round(float(proba[1]) * 100, 1)

    at_risk = prediction == 1
    return jsonify({
        "at_risk": at_risk,
        "risk_probability": risk_probability,
        "message": (
            "Indicators suggest an elevated risk of heart disease. Please consult a "
            "cardiologist and bring a recent medical report."
            if at_risk else
            "Indicators suggest a low risk of heart disease based on the values entered. "
            "Regular checkups are still recommended."
        ),
    })


ASSISTANT_KEYWORDS = [
    (["fever", "temperature"], "For fever: rest, stay hydrated, and take paracetamol if needed. "
        "See a doctor if fever exceeds 39°C, lasts more than 3 days, or comes with severe symptoms."),
    (["heart", "chest pain", "cardiac"], "Chest pain, especially with sweating or breathlessness, can signal "
        "a cardiac emergency. If you suspect a heart attack, call emergency services immediately."),
    (["headache", "migraine"], "For headaches: rest in a quiet dark room, stay hydrated, and avoid screens. "
        "Frequent or severe headaches should be checked by a doctor."),
    (["cough", "cold", "flu"], "For cough/cold: warm fluids, rest, and steam inhalation help. "
        "See a doctor if breathing becomes difficult or symptoms last beyond a week."),
    (["rash", "itch", "allergy", "skin"], "For skin rashes or itching: avoid the suspected trigger, keep the area "
        "clean, and consider an antihistamine. Seek care if it spreads or you have trouble breathing."),
    (["stomach", "vomit", "diarrhea", "food poisoning"], "For stomach upset: sip oral rehydration solution, "
        "eat light food, and rest. Seek care if vomiting/diarrhea is severe or persistent."),
    (["blood pressure", "hypertension", "bp"], "For high blood pressure: reduce salt intake, manage stress, "
        "exercise regularly, and take prescribed medication consistently."),
    (["pregnant", "pregnancy"], "For pregnancy-related concerns, please consult your OB-GYN directly — "
        "this assistant cannot safely guide pregnancy care."),
]

ASSISTANT_FALLBACK = (
    "I can share general health guidance, but I'm not a substitute for a licensed doctor. "
    "Could you tell me more about the specific symptom you're experiencing?"
)


def gemini_reply(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-1.5-flash:generateContent?key={api_key}")
        body = json_lib.dumps({
            "contents": [{"parts": [{
                "text": "You are a cautious health assistant. Give brief, safe general "
                        "guidance and always recommend seeing a doctor for anything serious. "
                        f"User question: {prompt}"
            }]}]
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json_lib.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


@app.route("/assistant", methods=["POST"])
def assistant():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please type a question."}), 400

    reply = gemini_reply(prompt)
    if reply is None:
        lowered = prompt.lower()
        reply = ASSISTANT_FALLBACK
        for keywords, response in ASSISTANT_KEYWORDS:
            if any(k in lowered for k in keywords):
                reply = response
                break

    return jsonify({"reply": reply})


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
