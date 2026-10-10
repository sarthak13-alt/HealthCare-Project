# Healthcare Data Warehousing & Mining PBL

A complete full-stack web application for analyzing 150,000+ patient records using ETL pipelines, machine learning, and interactive dashboards.

## Features

- **Interactive Dashboard** — 12+ real-time charts visualizing patient data, department distributions, vitals, risk analysis, and more
- **Dataset Explorer** — Browse, search, and filter all 150,000+ records with pagination
- **Data Preprocessing** — Full ETL pipeline (Extract → Transform → Load) with detailed quality reports
- **ML Prediction** — Predict symptom severity using trained classification models
- **Model Performance** — Compare Random Forest, Gradient Boosting, and Logistic Regression with confusion matrices and feature importance

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite |
| ML | scikit-learn, pandas, numpy |
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| ETL | Custom Python pipeline |

## Project Structure

```
healthcare-dwm-pbl/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── setup.bat               # Windows setup script
├── run.bat                 # Windows run script
├── data/
│   ├── raw/                # Place CSV here
│   └── processed/          # Cleaned data output
├── database/               # SQLite database (auto-created)
├── etl/                    # ETL pipeline modules
│   ├── extract.py          # Data extraction
│   ├── transform.py        # Data cleaning/transformation
│   └── load.py             # Load to SQLite/CSV
├── ml/                     # Machine learning modules
│   ├── preprocess.py       # Feature engineering
│   ├── train.py            # Model training
│   └── predict.py          # Prediction logic
├── models/                 # Saved ML models (auto-created)
├── static/
│   ├── css/style.css       # Application styles
│   └── js/                 # Frontend JavaScript
└── templates/              # HTML templates
```

## Quick Start

### 1. Setup

```batch
setup.bat
```

This creates a virtual environment and installs all dependencies.

### 2. Add Data

Place `healthcare_raw_data_150000.csv` in the `data/raw/` folder.

### 3. Run

```batch
run.bat
```

The application starts at **http://localhost:5000**

### 4. Use the Application

1. Go to **Preprocessing** page → Click "Run ETL Pipeline"
2. Go to **Models** page → Click "Train All Models"
3. Explore the **Dashboard**, **Dataset**, and **Prediction** pages

## Pages

| Page | Description |
|------|-------------|
| Home | Project overview and navigation |
| Dashboard | 12+ interactive charts with real data |
| Dataset | Searchable, filterable data table |
| Preprocessing | ETL pipeline with quality reports |
| Prediction | ML-powered severity prediction |
| Models | Model training and performance comparison |

## ML Models

Three classifiers are trained to predict symptom severity (Mild/Moderate/Severe):

- **Random Forest** — 200 estimators, max depth 15
- **Gradient Boosting** — 150 estimators, learning rate 0.1
- **Logistic Regression** — Multinomial with L2 regularization

The best model is automatically selected based on test accuracy.

## ETL Pipeline

1. **Extract** — Load raw CSV from `data/raw/`
2. **Transform** — Standardize casing, remove duplicates, impute missing values, cap outliers, engineer features
3. **Load** — Store in SQLite database and processed CSV

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| patient_id | int | Unique patient identifier |
| age | int | Patient age (18-80) |
| gender | str | Male/Female |
| symptoms | str | Reported symptoms |
| temperature | float | Body temperature (°F) |
| duration_days | int | Symptom duration |
| bp_systolic | int | Systolic blood pressure |
| bp_diastolic | int | Diastolic blood pressure |
| heart_rate | int | Heart rate (bpm) |
| oxygen_saturation | float | SpO2 (%) |
| pain_level | int | Pain scale (0-10) |
| symptom_severity | str | Mild/Moderate/Severe |
| chronic_condition | str | Yes/No |
| department | str | Hospital department |

## Requirements

- Python 3.9+
- Windows (for .bat files) or manual setup

## License

This project is created for educational purposes as a PBL (Project-Based Learning) assignment.
