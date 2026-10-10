"""
Healthcare DWM PBL - Central Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_CSV = os.path.join(DATA_RAW_DIR, "healthcare_raw_data_150000.csv")
CLEAN_CSV = os.path.join(DATA_PROCESSED_DIR, "healthcare_clean.csv")

# Database
DB_PATH = os.path.join(BASE_DIR, "database", "healthcare.db")

# Models
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Ensure directories exist
for d in [DATA_RAW_DIR, DATA_PROCESSED_DIR, os.path.join(BASE_DIR, "database"), MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

# Flask
SECRET_KEY = "healthcare-dwm-pbl-2024-secret"
DEBUG = True
PORT = 5000
