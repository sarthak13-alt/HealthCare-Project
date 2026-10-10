"""
ML - Training Module
Trains multiple classifiers to predict hospital department from patient vitals.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from config import MODELS_DIR
from ml.preprocess import prepare_features


def train_all_models(df):
    """Train multiple models to predict department and return results."""
    # Use a sample for faster training (stratified to maintain class balance)
    if len(df) > 20000:
        indices = []
        for dept, group in df.groupby("department"):
            n = min(len(group), 2000)
            indices.extend(group.sample(n=n, random_state=42).index.tolist())
        df = df.loc[indices].reset_index(drop=True)

    X, y, le_target, encoders, feature_names, numeric_features = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=50, max_depth=10, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=200, random_state=42
        ),
    }

    results = {}
    best_model = None
    best_score = 0
    best_name = ""

    for name, model in models.items():
        print(f"  Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()

        cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring="accuracy")

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "confusion_matrix": cm,
            "classification_report": classification_report(
                y_test, y_pred, target_names=le_target.classes_, zero_division=0
            ),
        }

        if acc > best_score:
            best_score = acc
            best_model = model
            best_name = name

    # Feature importance from best model
    feature_importance = None
    if hasattr(best_model, "feature_importances_"):
        importance = best_model.feature_importances_
        feature_importance = sorted(
            zip(feature_names, [round(float(i), 4) for i in importance]),
            key=lambda x: x[1], reverse=True
        )

    # Save model and artifacts
    joblib.dump(best_model, os.path.join(MODELS_DIR, "severity_model.pkl"))
    joblib.dump(le_target, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    joblib.dump(encoders, os.path.join(MODELS_DIR, "encoders.pkl"))
    joblib.dump(feature_names, os.path.join(MODELS_DIR, "feature_names.pkl"))
    joblib.dump(numeric_features, os.path.join(MODELS_DIR, "numeric_features.pkl"))

    report = {
        "best_model": best_name,
        "best_accuracy": round(float(best_score), 4),
        "all_models": results,
        "feature_importance": feature_importance,
        "classes": list(le_target.classes_),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "target_variable": "department",
    }

    with open(os.path.join(MODELS_DIR, "training_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    return report


def load_trained_model():
    """Load the trained model and associated artifacts."""
    model_path = os.path.join(MODELS_DIR, "severity_model.pkl")
    if not os.path.exists(model_path):
        return None, None, None, None, None

    model = joblib.load(model_path)
    le_target = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    encoders = joblib.load(os.path.join(MODELS_DIR, "encoders.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_DIR, "feature_names.pkl"))
    numeric_features = joblib.load(os.path.join(MODELS_DIR, "numeric_features.pkl"))

    return model, le_target, encoders, feature_names, numeric_features


if __name__ == "__main__":
    from etl.extract import extract_data
    from etl.transform import transform_data

    df = extract_data()
    clean_df, _ = transform_data(df)
    report = train_all_models(clean_df)
    print(f"Best Model: {report['best_model']} (Accuracy: {report['best_accuracy']})")
    for name, metrics in report["all_models"].items():
        print(f"  {name}: acc={metrics['accuracy']}, f1={metrics['f1_score']}")
