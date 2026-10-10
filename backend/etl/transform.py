"""
ETL - Transform Module
Cleans and standardizes the raw healthcare data.
"""
import pandas as pd
import numpy as np


def standardize_casing(df):
    """Fix inconsistent casing in categorical columns."""
    df = df.copy()
    for col in ["gender", "symptom_severity", "chronic_condition"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()
    return df


def handle_missing_values(df):
    """Impute missing values with appropriate strategies."""
    df = df.copy()

    # Numeric columns: fill with median
    numeric_cols = [
        "age", "temperature", "duration_days", "bp_systolic",
        "bp_diastolic", "heart_rate", "oxygen_saturation", "pain_level"
    ]
    for col in numeric_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # Categorical columns: fill with mode
    cat_cols = ["gender", "symptoms", "symptom_severity", "chronic_condition", "department"]
    for col in cat_cols:
        if col in df.columns:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    return df


def remove_duplicates(df):
    """Remove duplicate rows."""
    return df.drop_duplicates().reset_index(drop=True)


def handle_outliers(df):
    """Cap outliers using IQR method for key vitals."""
    df = df.copy()

    # Oxygen saturation should be 70-100
    if "oxygen_saturation" in df.columns:
        df["oxygen_saturation"] = df["oxygen_saturation"].clip(70, 100)

    # Temperature: 93-106 F
    if "temperature" in df.columns:
        df["temperature"] = df["temperature"].clip(93, 106)

    # Heart rate: 30-220
    if "heart_rate" in df.columns:
        df["heart_rate"] = df["heart_rate"].clip(30, 220)

    # BP systolic: 70-250, diastolic: 40-150
    if "bp_systolic" in df.columns:
        df["bp_systolic"] = df["bp_systolic"].clip(70, 250)
    if "bp_diastolic" in df.columns:
        df["bp_diastolic"] = df["bp_diastolic"].clip(40, 150)

    # Age: 18-100
    if "age" in df.columns:
        df["age"] = df["age"].clip(18, 100)

    # Pain level: 0-10
    if "pain_level" in df.columns:
        df["pain_level"] = df["pain_level"].clip(0, 10)

    return df


def add_derived_features(df):
    """Add computed columns for analysis."""
    df = df.copy()

    # BP category
    def bp_category(row):
        sys, dia = row["bp_systolic"], row["bp_diastolic"]
        if sys < 120 and dia < 80:
            return "Normal"
        elif sys < 130 and dia < 80:
            return "Elevated"
        elif sys < 140 or dia < 90:
            return "High Stage 1"
        else:
            return "High Stage 2"

    df["bp_category"] = df.apply(bp_category, axis=1)

    # Fever flag
    df["has_fever"] = (df["temperature"] > 100.4).astype(int)

    # Age group
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 30, 45, 60, 100],
        labels=["18-30", "31-45", "46-60", "60+"]
    ).astype(str)

    # Risk score (composite)
    df["risk_score"] = (
        (df["pain_level"] / 10) * 0.3 +
        ((df["temperature"] - 98.6).abs() / 8) * 0.2 +
        ((df["heart_rate"] - 80).abs() / 80) * 0.2 +
        ((100 - df["oxygen_saturation"]) / 30).clip(0, 1) * 0.3
    ).round(3)

    return df


def transform_data(df):
    """Run full transformation pipeline, return cleaned df + report."""
    report = {
        "rows_before": int(len(df)),
        "steps": []
    }

    # Step 1: Standardize casing
    df = standardize_casing(df)
    report["steps"].append({"step": "Standardize Casing", "description": "Fixed inconsistent text casing in gender, severity, chronic_condition"})

    # Step 2: Remove duplicates
    before = len(df)
    df = remove_duplicates(df)
    removed = before - len(df)
    report["steps"].append({"step": "Remove Duplicates", "description": f"Removed {removed} duplicate rows", "count": removed})

    # Step 3: Handle missing values
    missing_before = int(df.isnull().sum().sum())
    df = handle_missing_values(df)
    report["steps"].append({"step": "Impute Missing Values", "description": f"Filled {missing_before} missing values (median for numeric, mode for categorical)", "count": missing_before})

    # Step 4: Handle outliers
    df = handle_outliers(df)
    report["steps"].append({"step": "Handle Outliers", "description": "Capped physiologically impossible values (SpO2, temp, HR, BP, age, pain)"})

    # Step 5: Add derived features
    df = add_derived_features(df)
    report["steps"].append({"step": "Feature Engineering", "description": "Added bp_category, has_fever, age_group, risk_score"})

    report["rows_after"] = int(len(df))
    report["columns_after"] = int(len(df.columns))

    return df, report


if __name__ == "__main__":
    from etl.extract import extract_data
    df = extract_data()
    clean_df, report = transform_data(df)
    print(f"Transformed: {report['rows_before']} -> {report['rows_after']} rows")
    for step in report["steps"]:
        print(f"  - {step['step']}: {step['description']}")
