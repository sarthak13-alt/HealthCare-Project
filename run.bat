@echo off
echo ============================================
echo   Healthcare DWM PBL - Starting Server
echo ============================================
echo.

REM Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [WARN] Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check for raw CSV
if not exist "backend\data\raw\healthcare_raw_data_150000.csv" (
    echo [INFO] Generating raw dataset...
    python backend\generate_dataset.py
)

echo.
echo Starting Flask server at http://localhost:5000
echo Press Ctrl+C to stop
echo.

python backend\app.py

pause
