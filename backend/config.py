"""
Healthcare DWM PBL - Central Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if running in a read-only serverless environment (e.g. Vercel)
IS_READ_ONLY = False
try:
    test_dir = os.path.join(BASE_DIR, "_test_write")
    os.makedirs(test_dir, exist_ok=True)
    os.rmdir(test_dir)
except Exception:
    IS_READ_ONLY = True

if IS_READ_ONLY:
    WORK_DIR = "/tmp/healthcare"
else:
    WORK_DIR = BASE_DIR

# Data paths
DATA_RAW_DIR = os.path.join(WORK_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(WORK_DIR, "data", "processed")
RAW_CSV = os.path.join(DATA_RAW_DIR, "healthcare_raw_data_150000.csv")
CLEAN_CSV = os.path.join(DATA_PROCESSED_DIR, "healthcare_clean.csv")

# Database
DB_PATH = os.path.join(WORK_DIR, "database", "healthcare.db")

# Models
MODELS_DIR = os.path.join(WORK_DIR, "models")

# Ensure directories exist
for d in [DATA_RAW_DIR, DATA_PROCESSED_DIR, os.path.join(WORK_DIR, "database"), MODELS_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass

# Flask
SECRET_KEY = "healthcare-dwm-pbl-2024-secret"
DEBUG = True
PORT = 5000
