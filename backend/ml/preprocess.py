"""
ML - Preprocessing Module
Feature engineering and preparation for machine learning.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


def prepare_features(df, target_col="department"):
    """Prepare feature matrix X and target y from cleaned dataframe."""
    df = df.copy()

    # Encode target
    le_target = LabelEncoder()
    y = le_target.fit_transform(df[target_col])

    # Select features
    numeric_features = [
        "age", "temperature", "duration_days", "bp_systolic",
        "bp_diastolic", "heart_rate", "oxygen_saturation", "pain_level"
    ]

    # Encode categorical features
    cat_features = ["gender", "chronic_condition", "department", "symptoms"]
    encoders = {}

    X_numeric = df[numeric_features].values

    X_categorical = []
    for col in cat_features:
        le = LabelEncoder()
        encoded = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        X_categorical.append(encoded.reshape(-1, 1))

    X_cat = np.hstack(X_categorical) if X_categorical else np.empty((len(df), 0))

    # Combine
    X = np.hstack([X_numeric, X_cat])

    feature_names = numeric_features + cat_features

    return X, y, le_target, encoders, feature_names, numeric_features


def prepare_single_record(record_dict, encoders, numeric_features, feature_names):
    """Prepare a single record for prediction."""
    values = []

    for feat in feature_names:
        if feat in numeric_features:
            values.append(float(record_dict.get(feat, 0)))
        else:
            le = encoders.get(feat)
            val = str(record_dict.get(feat, ""))
            if le is not None:
                try:
                    encoded = le.transform([val])[0]
                except ValueError:
                    # Unknown category - use most frequent (0 after encoding)
                    encoded = 0
                values.append(encoded)
            else:
                values.append(0)

    return np.array(values).reshape(1, -1)
