"""
ML - Prediction Module
Makes predictions using the trained model.
"""
import numpy as np
from ml.preprocess import prepare_single_record
from ml.train import load_trained_model


def predict_severity(record_dict):
    """Predict symptom severity for a single patient record."""
    model, le_target, encoders, feature_names, numeric_features = load_trained_model()

    if model is None:
        return {"error": "Model not trained yet. Train the model first."}

    X = prepare_single_record(record_dict, encoders, numeric_features, feature_names)

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    severity = le_target.inverse_transform([prediction])[0]
    prob_dict = {
        le_target.inverse_transform([i])[0]: round(float(p), 4)
        for i, p in enumerate(probabilities)
    }

    return {
        "severity": severity,
        "confidence": round(float(probabilities[prediction]), 4),
        "probabilities": prob_dict,
    }


def get_model_info():
    """Get information about the trained model."""
    import os
    import json
    from config import MODELS_DIR

    report_path = os.path.join(MODELS_DIR, "training_report.json")
    if not os.path.exists(report_path):
        return None

    with open(report_path, "r") as f:
        return json.load(f)
