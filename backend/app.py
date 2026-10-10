"""
Healthcare Data Warehousing & Mining PBL
Main Flask Application
"""
import os
import json
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from config import DB_PATH, RAW_CSV, DATA_RAW_DIR, PORT, DEBUG
from etl.extract import extract_data, profile_data
from etl.transform import transform_data
from etl.load import load_to_csv, load_to_sqlite, run_full_etl
from ml.train import train_all_models, load_trained_model
from ml.predict import predict_severity, get_model_info

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static")
)



# ─── Helpers ───────────────────────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_data_ready():
    """Check if ETL has been run and data is in SQLite."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def ensure_etl():
    """Run ETL if data not yet loaded."""
    if not check_data_ready():
        if not os.path.exists(RAW_CSV):
            try:
                from generate_dataset import generate_dataset
                generate_dataset(num_rows=2000, output_path=RAW_CSV)
            except Exception as e:
                print(f"[WARN] Failed to auto-generate raw CSV: {e}")
                return False
        try:
            run_full_etl(RAW_CSV)
        except Exception as e:
            print(f"[WARN] Failed to run ETL: {e}")
            return False
    return True



# ─── Page Routes ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/dataset")
def dataset():
    return render_template("dataset.html")


@app.route("/preprocessing")
def preprocessing():
    return render_template("preprocessing.html")


@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


@app.route("/models")
def models():
    return render_template("models.html")


# ─── API Routes ───────────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Upload a CSV dataset."""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not file.filename.endswith(".csv"):
            return jsonify({"success": False, "error": "Only CSV files are allowed"}), 400

        # Save to data/raw/
        os.makedirs(DATA_RAW_DIR, exist_ok=True)
        filepath = os.path.join(DATA_RAW_DIR, "healthcare_raw_data_150000.csv")
        file.save(filepath)

        return jsonify({
            "success": True,
            "message": f"File uploaded: {file.filename}",
            "path": filepath,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/etl/run", methods=["POST"])
def api_run_etl():
    """Run the full ETL pipeline."""
    try:
        if not os.path.exists(RAW_CSV):
            return jsonify({
                "success": False,
                "error": f"CSV not found. Place healthcare_raw_data_150000.csv in {DATA_RAW_DIR}"
            }), 400

        result = run_full_etl()
        return jsonify({
            "success": True,
            "profile": result["profile"],
            "transform": result["transform"],
            "csv_output": result["csv_output"],
            "db_output": result["db_output"],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/etl/status")
def api_etl_status():
    """Check ETL status."""
    raw_exists = os.path.exists(RAW_CSV)
    db_exists = check_data_ready()
    return jsonify({
        "raw_csv_exists": raw_exists,
        "db_ready": db_exists,
        "raw_path": RAW_CSV if raw_exists else None,
    })


@app.route("/api/data/profile")
def api_data_profile():
    """Get data profile (runs ETL if needed)."""
    try:
        if not ensure_etl():
            return jsonify({"error": "No data available"}), 400

        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM patients", conn)
        conn.close()

        profile = {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "columns": list(df.columns),
            "missing": {col: int(df[col].isnull().sum()) for col in df.columns},
            "duplicates": int(df.duplicated().sum()),
        }
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/summary")
def api_data_summary():
    """Get summary statistics for dashboard."""
    try:
        if not ensure_etl():
            return jsonify({"error": "No data available"}), 400

        conn = get_db_connection()

        # Department distribution
        dept = pd.read_sql(
            "SELECT department, COUNT(*) as count FROM patients GROUP BY department ORDER BY count DESC",
            conn
        ).to_dict("records")

        # Severity distribution
        sev = pd.read_sql(
            "SELECT symptom_severity, COUNT(*) as count FROM patients GROUP BY symptom_severity ORDER BY count DESC",
            conn
        ).to_dict("records")

        # Gender distribution
        gender = pd.read_sql(
            "SELECT gender, COUNT(*) as count FROM patients GROUP BY gender ORDER BY count DESC",
            conn
        ).to_dict("records")

        # Age distribution
        age = pd.read_sql(
            "SELECT age_group, COUNT(*) as count FROM patients GROUP BY age_group ORDER BY age_group",
            conn
        ).to_dict("records")

        # Chronic condition
        chronic = pd.read_sql(
            "SELECT chronic_condition, COUNT(*) as count FROM patients GROUP BY chronic_condition",
            conn
        ).to_dict("records")

        # Vitals averages by department
        vitals = pd.read_sql(
            """SELECT department,
                ROUND(AVG(temperature),1) as avg_temp,
                ROUND(AVG(heart_rate),1) as avg_hr,
                ROUND(AVG(oxygen_saturation),1) as avg_spo2,
                ROUND(AVG(bp_systolic),1) as avg_bp_sys,
                ROUND(AVG(bp_diastolic),1) as avg_bp_dia,
                ROUND(AVG(pain_level),1) as avg_pain
            FROM patients GROUP BY department ORDER BY department""",
            conn
        ).to_dict("records")

        # Top symptoms
        symptoms = pd.read_sql(
            "SELECT symptoms, COUNT(*) as count FROM patients GROUP BY symptoms ORDER BY count DESC LIMIT 15",
            conn
        ).to_dict("records")

        # BP category distribution
        bp_cat = pd.read_sql(
            "SELECT bp_category, COUNT(*) as count FROM patients GROUP BY bp_category ORDER BY count DESC",
            conn
        ).to_dict("records")

        # Severity by department (stacked bar)
        sev_dept = pd.read_sql(
            """SELECT department, symptom_severity, COUNT(*) as count
            FROM patients GROUP BY department, symptom_severity ORDER BY department""",
            conn
        ).to_dict("records")

        # Risk score distribution
        risk = pd.read_sql(
            """SELECT
                CASE
                    WHEN risk_score < 0.25 THEN 'Low'
                    WHEN risk_score < 0.5 THEN 'Moderate'
                    WHEN risk_score < 0.75 THEN 'High'
                    ELSE 'Critical'
                END as risk_level,
                COUNT(*) as count
            FROM patients GROUP BY risk_level
            ORDER BY CASE risk_level
                WHEN 'Low' THEN 1 WHEN 'Moderate' THEN 2
                WHEN 'High' THEN 3 WHEN 'Critical' THEN 4 END""",
            conn
        ).to_dict("records")

        # Fever stats
        fever = pd.read_sql(
            "SELECT has_fever, COUNT(*) as count FROM patients GROUP BY has_fever",
            conn
        ).to_dict("records")

        # Total stats
        total = pd.read_sql(
            """SELECT COUNT(*) as total_patients,
                ROUND(AVG(age),1) as avg_age,
                ROUND(AVG(temperature),1) as avg_temp,
                ROUND(AVG(heart_rate),1) as avg_hr,
                ROUND(AVG(oxygen_saturation),1) as avg_spo2,
                ROUND(AVG(pain_level),1) as avg_pain,
                SUM(CASE WHEN chronic_condition='Yes' THEN 1 ELSE 0 END) as chronic_count,
                SUM(CASE WHEN has_fever=1 THEN 1 ELSE 0 END) as fever_count
            FROM patients""",
            conn
        ).to_dict("records")[0]

        conn.close()

        return jsonify({
            "departments": dept,
            "severity": sev,
            "gender": gender,
            "age_groups": age,
            "chronic": chronic,
            "vitals_by_dept": vitals,
            "top_symptoms": symptoms,
            "bp_categories": bp_cat,
            "severity_by_dept": sev_dept,
            "risk_levels": risk,
            "fever": fever,
            "totals": total,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/records")
def api_data_records():
    """Get paginated patient records."""
    try:
        if not ensure_etl():
            return jsonify({"error": "No data available"}), 400

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 25, type=int)
        search = request.args.get("search", "", type=str)
        dept_filter = request.args.get("department", "", type=str)
        sev_filter = request.args.get("severity", "", type=str)

        offset = (page - 1) * per_page

        conn = get_db_connection()

        where_clauses = []
        params = []

        if search:
            where_clauses.append("(patient_id LIKE ? OR symptoms LIKE ? OR department LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if dept_filter:
            where_clauses.append("department = ?")
            params.append(dept_filter)

        if sev_filter:
            where_clauses.append("symptom_severity = ?")
            params.append(sev_filter)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Total count
        count_query = f"SELECT COUNT(*) FROM patients WHERE {where_sql}"
        total = conn.execute(count_query, params).fetchone()[0]

        # Records
        query = f"SELECT * FROM patients WHERE {where_sql} ORDER BY patient_id LIMIT ? OFFSET ?"
        rows = conn.execute(query, params + [per_page, offset]).fetchall()

        conn.close()

        records = [dict(row) for row in rows]

        return jsonify({
            "records": records,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/filters")
def api_data_filters():
    """Get filter options for dataset page."""
    try:
        if not ensure_etl():
            return jsonify({"error": "No data available"}), 400

        conn = get_db_connection()
        departments = [r[0] for r in conn.execute("SELECT DISTINCT department FROM patients ORDER BY department").fetchall()]
        severities = [r[0] for r in conn.execute("SELECT DISTINCT symptom_severity FROM patients ORDER BY symptom_severity").fetchall()]
        symptoms = [r[0] for r in conn.execute("SELECT DISTINCT symptoms FROM patients ORDER BY symptoms").fetchall()]
        conn.close()

        return jsonify({
            "departments": departments,
            "severities": severities,
            "symptoms": symptoms,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/preprocessing/info")
def api_preprocessing_info():
    """Get preprocessing pipeline information."""
    try:
        if not os.path.exists(RAW_CSV):
            return jsonify({"error": "No raw data available"}), 400

        raw_df = extract_data()
        profile = profile_data(raw_df)

        # Run transform to get report
        clean_df, transform_report = transform_data(raw_df)

        return jsonify({
            "raw_profile": profile,
            "transform_report": transform_report,
            "clean_rows": int(len(clean_df)),
            "clean_columns": int(len(clean_df.columns)),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ml/train", methods=["POST"])
def api_train():
    """Train ML models."""
    try:
        if not ensure_etl():
            return jsonify({"error": "No data available. Run ETL first."}), 400

        conn = get_db_connection()
        # Sample at query level for speed
        df = pd.read_sql(
            "SELECT * FROM patients ORDER BY RANDOM() LIMIT 5000", conn
        )
        conn.close()

        report = train_all_models(df)
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ml/status")
def api_ml_status():
    """Check if model is trained."""
    info = get_model_info()
    return jsonify({
        "trained": info is not None,
        "info": info,
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Make a severity prediction."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = predict_severity(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict/batch", methods=["POST"])
def api_predict_batch():
    """Make predictions for multiple records."""
    try:
        data = request.get_json()
        if not data or "records" not in data:
            return jsonify({"error": "No records provided"}), 400

        results = []
        for record in data["records"]:
            result = predict_severity(record)
            results.append(result)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Healthcare Data Warehousing & Mining PBL")
    print("=" * 60)

    # Check for raw CSV
    if os.path.exists(RAW_CSV):
        print(f"[OK] Raw CSV found: {RAW_CSV}")
    else:
        print(f"[WARN] Raw CSV not found at {RAW_CSV}")
        print(f"       Place healthcare_raw_data_150000.csv in data/raw/")

    # Auto-run ETL if CSV exists and DB doesn't
    if os.path.exists(RAW_CSV) and not check_data_ready():
        print("[INFO] Running ETL pipeline...")
        try:
            run_full_etl()
            print("[OK] ETL complete. Database ready.")
        except Exception as e:
            print(f"[ERROR] ETL failed: {e}")

    if check_data_ready():
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        conn.close()
        print(f"[OK] Database ready: {count} records")
    else:
        print("[WARN] Database not ready. Run ETL via the Preprocessing page.")

    print(f"\n  Starting server at http://localhost:{PORT}")
    print("=" * 60)

    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
