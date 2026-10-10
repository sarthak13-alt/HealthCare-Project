"""
ETL - Load Module
Loads cleaned data into SQLite database and processed CSV.
"""
import sqlite3
import pandas as pd
import os
from config import DB_PATH, CLEAN_CSV


def load_to_csv(df, path=None):
    """Save cleaned data to processed CSV."""
    path = path or CLEAN_CSV
    df.to_csv(path, index=False)
    return path


def load_to_sqlite(df, db_path=None):
    """Load cleaned data into SQLite database."""
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)

    conn = sqlite3.connect(path)
    df.to_sql("patients", conn, if_exists="replace", index=False)

    # Create indexes for common queries
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_department ON patients(department)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON patients(symptom_severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gender ON patients(gender)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_age ON patients(age)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chronic ON patients(chronic_condition)")
    conn.commit()
    conn.close()
    return path


def run_full_etl(csv_path=None):
    """Execute complete ETL pipeline: Extract -> Transform -> Load."""
    from etl.extract import extract_data, profile_data
    from etl.transform import transform_data

    # Extract
    raw_df = extract_data(csv_path)
    profile = profile_data(raw_df)

    # Transform
    clean_df, transform_report = transform_data(raw_df)

    # Load
    csv_out = load_to_csv(clean_df)
    db_out = load_to_sqlite(clean_df)

    return {
        "profile": profile,
        "transform": transform_report,
        "csv_output": csv_out,
        "db_output": db_out,
        "clean_df": clean_df,
    }


if __name__ == "__main__":
    result = run_full_etl()
    print(f"ETL Complete!")
    print(f"  CSV: {result['csv_output']}")
    print(f"  DB:  {result['db_output']}")
    print(f"  Rows: {result['transform']['rows_after']}")
