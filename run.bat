@echo off
REM Internship Tracker - Run Script (Windows)
REM Start the app: run.bat

call venv\Scripts\activate
echo 🚀 Starting Internship Tracker...
echo    Open: http://127.0.0.1:1453
echo    Press Ctrl+C to stop
echo.
python app.py
