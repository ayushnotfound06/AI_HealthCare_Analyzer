# IntelliHealthcare — Intelligent Healthcare Symptom Analysis System

3rd Year - Minor Project · Department of Informatics & Systems, School of Systems &
Technology, University of Management and Technology (UMT), Lahore, Pakistan.

**Team:** Ayush Dubey (8824103091), Yash Sharma (8824103083), Aadi Jain  (8824103003), Ashutosh Chauhan (8824103096)

## Problem

Accurate and timely diagnosis of diseases based on patient symptoms is a
recurring challenge in regions with limited medical infrastructure. Even
experienced doctors can make errors under high patient volume, and many
areas simply lack access to specialists. This project explores whether a
symptom-based machine learning classifier, paired with a simple web
interface, can give doctors and patients a fast, structured second opinion.

## What it does

- **Symptom Tracker** — the user selects reported symptoms from a searchable
  list; a Decision Tree classifier predicts the most likely condition among
  15 supported diseases and returns an urgency label (emergency / see a
  doctor / self-care) alongside plain-language guidance.
- **Heart Disease Detector** — the user enters 13 clinical values from a
  recent medical report (blood pressure, cholesterol, ECG results, etc.); a
  Random Forest classifier estimates heart disease risk probability.
- **Health Assistant** — a lightweight chat widget that answers general
  symptom questions, with an optional live connection to the Gemini API.
- **Live stats page** — reports the actual held-out test accuracy of both
  models rather than a fixed number.

## Tech stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Backend    | Python, Flask                             |
| ML         | scikit-learn (Decision Tree, Random Forest), pandas, NumPy |
| Frontend   | HTML, CSS, vanilla JavaScript             |
| Data       | Custom CSV symptom/disease and heart-risk datasets (see note below) |

## Architecture

```
Browser (UI)  <-- HTTP/JSON -->  Flask app (app.py)
                                     |
                          ┌──────────┴──────────┐
                    disease_model.pkl      heart_model.pkl
                 (Decision Tree Classifier) (Random Forest Classifier)
```

## Project structure

```
IntelliHealthcare/
├── app.py                   # Flask routes & inference logic
├── generate_data.py         # Builds the training datasets
├── train_disease_model.py   # Trains + pickles the symptom classifier
├── train_heart_model.py     # Trains + pickles the heart risk classifier
├── data/                    # Disease_Symptoms.csv, heart.csv
├── models/                  # Trained model artifacts (.pkl)
├── templates/                # Jinja2 templates (Home, Detector, Stats, About, 404)
└── static/                  # CSS, JS, favicon
```

## Running locally

```bash
pip install -r requirements.txt
python generate_data.py          # builds data/Disease_Symptoms.csv and data/heart.csv
python train_disease_model.py    # trains and saves models/disease_model.pkl
python train_heart_model.py      # trains and saves models/heart_model.pkl
python app.py                    # starts the app on http://127.0.0.1:5000
```

Optional: set `GEMINI_API_KEY` as an environment variable to let the health
assistant call the Gemini API instead of its offline rule-based fallback.

## Model performance

Accuracy is computed on a stratified 80/20 held-out split and displayed live
on the Current-Stat's page — it is not hardcoded.

| Model                | Algorithm              | Test Accuracy |
|-----------------------|------------------------|----------------|
| Symptom classifier    | Decision Tree          | ~83%           |
| Heart risk classifier | Random Forest          | ~80%           |

## A note on the dataset

The symptom-disease and heart-risk datasets used here are custom-built
(`generate_data.py`) rather than sourced from a public repository: they
encode the same 15 conditions, 49 symptoms, and 13 clinical features
described in the project documentation, with realistic co-occurrence
patterns per condition. They are suitable for demonstrating the pipeline
end-to-end but have not been clinically validated — see Limitations below.

## Limitations

- Predictions are based on self-reported symptoms only and are **not** a
  substitute for professional medical diagnosis.
- The datasets are synthetic; a production deployment would need a
  clinically validated dataset and sign-off from medical professionals.
- No authentication, rate-limiting, or persistent storage is implemented —
  this is a demonstration-grade build, not a production system.

## Future work

1. Integrate with live medical databases / electronic health records.
2. Replace the synthetic dataset with a clinically validated one.
3. Expand disease and symptom coverage.
4. Package as a mobile application for wider reach in underserved areas.
