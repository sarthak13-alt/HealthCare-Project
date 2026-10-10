"""
ETL - Extract Module
Reads raw CSV data from data/raw/ and performs initial profiling.
"""
import pandas as pd
import os
from config import RAW_CSV


def extract_data(csv_path=None):
    """Load raw CSV into a DataFrame."""
    path = csv_path or RAW_CSV
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Raw CSV not found at {path}. "
            "Place healthcare_raw_data_150000.csv in data/raw/"
        )
    df = pd.read_csv(path)
    return df


def profile_data(df):
    """Generate a data quality profile report."""
    report = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": {col: int(df[col].isnull().sum()) for col in df.columns},
        "missing_pct": {
            col: round(float(df[col].isnull().sum()) / len(df) * 100, 2)
            for col in df.columns
        },
        "duplicates": int(df.duplicated().sum()),
        "numeric_summary": {},
        "categorical_unique": {},
    }

    for col in df.select_dtypes(include=["number"]).columns:
        report["numeric_summary"][col] = {
            "min": float(df[col].min()) if not df[col].isnull().all() else None,
            "max": float(df[col].max()) if not df[col].isnull().all() else None,
            "mean": round(float(df[col].mean()), 2) if not df[col].isnull().all() else None,
            "std": round(float(df[col].std()), 2) if not df[col].isnull().all() else None,
        }

    for col in df.select_dtypes(include=["object"]).columns:
        report["categorical_unique"][col] = int(df[col].nunique())

    return report


if __name__ == "__main__":
    df = extract_data()
    print(f"Extracted {len(df)} rows and {len(df.columns)} columns")
    report = profile_data(df)
    print(f"Missing values: {sum(report['missing'].values())}")
    print(f"Duplicates: {report['duplicates']}")
