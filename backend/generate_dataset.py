"""
Generate synthetic raw healthcare dataset for Healthcare DWM PBL
"""
import os
import numpy as np
import pandas as pd

def generate_dataset(num_rows=150000, output_path="data/raw/healthcare_raw_data_150000.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        print(f"[INFO] Dataset already exists at {output_path}")
        return

    print(f"[INFO] Generating synthetic healthcare dataset with {num_rows} records...")
    np.random.seed(42)

    departments = [
        "General Medicine", "Cardiology", "Pulmonology", "Emergency",
        "Neurology", "Orthopedics", "Gastroenterology"
    ]
    symptoms_list = [
        "Fever", "Cough", "Chest Pain", "Shortness of Breath", "Headache",
        "Fatigue", "Abdominal Pain", "Dizziness", "Joint Pain", "Nausea"
    ]
    genders = ["Male", "Female", "male", "female", "M", "F"] # Include raw dirty casing for ETL test
    severities = ["Mild", "Moderate", "Severe", "mild", "moderate", "severe"]
    chronic_options = ["Yes", "No", "yes", "no"]

    patient_ids = np.arange(1, num_rows + 1)
    ages = np.random.randint(18, 85, size=num_rows)
    gender_choice = np.random.choice(genders, size=num_rows, p=[0.45, 0.45, 0.03, 0.03, 0.02, 0.02])
    symptoms_choice = np.random.choice(symptoms_list, size=num_rows)
    temperatures = np.round(np.random.normal(98.6, 1.8, size=num_rows), 1)
    durations = np.random.randint(1, 31, size=num_rows)
    bp_sys = np.random.randint(95, 175, size=num_rows)
    bp_dia = np.random.randint(60, 115, size=num_rows)
    heart_rates = np.random.randint(55, 125, size=num_rows)
    o2_sats = np.round(np.random.normal(97.0, 2.5, size=num_rows), 1)
    o2_sats = np.clip(o2_sats, 75.0, 100.0)
    pain_levels = np.random.randint(0, 11, size=num_rows)
    severity_choice = np.random.choice(severities, size=num_rows)
    chronic_choice = np.random.choice(chronic_options, size=num_rows)

    # Department mapping logic based on symptom for realistic structure
    dept_map = {
        "Fever": "General Medicine",
        "Cough": "Pulmonology",
        "Chest Pain": "Cardiology",
        "Shortness of Breath": "Pulmonology",
        "Headache": "Neurology",
        "Fatigue": "General Medicine",
        "Abdominal Pain": "Gastroenterology",
        "Dizziness": "Neurology",
        "Joint Pain": "Orthopedics",
        "Nausea": "Gastroenterology"
    }
    dept_choice = [dept_map.get(s, np.random.choice(departments)) for s in symptoms_choice]
    # Introduce small random noise in department assignment
    noise_indices = np.random.choice(num_rows, size=int(num_rows * 0.15), replace=False)
    for idx in noise_indices:
        dept_choice[idx] = np.random.choice(departments)

    df = pd.DataFrame({
        "patient_id": patient_ids,
        "age": ages,
        "gender": gender_choice,
        "symptoms": symptoms_choice,
        "temperature": temperatures,
        "duration_days": durations,
        "bp_systolic": bp_sys,
        "bp_diastolic": bp_dia,
        "heart_rate": heart_rates,
        "oxygen_saturation": o2_sats,
        "pain_level": pain_levels,
        "symptom_severity": severity_choice,
        "chronic_condition": chronic_choice,
        "department": dept_choice
    })

    # Add a few missing values and duplicate rows for ETL to clean
    missing_indices = np.random.choice(num_rows, size=int(num_rows * 0.01), replace=False)
    df.loc[missing_indices, "temperature"] = np.nan
    missing_indices_o2 = np.random.choice(num_rows, size=int(num_rows * 0.005), replace=False)
    df.loc[missing_indices_o2, "oxygen_saturation"] = np.nan

    df.to_csv(output_path, index=False)
    print(f"[OK] Successfully generated {num_rows} raw dataset rows at {output_path}")

if __name__ == "__main__":
    generate_dataset()
