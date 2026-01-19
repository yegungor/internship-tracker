@echo off
REM Internship Tracker - Quick Setup Script (Windows)
REM Run this once after cloning: setup.bat

echo 🚀 Setting up Internship Tracker...

echo 📦 Creating virtual environment...
python -m venv venv

echo ✅ Activating virtual environment...
call venv\Scripts\activate

echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✨ Setup complete!
echo.
echo To run the app:
echo   venv\Scripts\activate
echo   python app.py
echo.
echo Then open: http://127.0.0.1:1453
