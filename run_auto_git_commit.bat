@echo off
setlocal

REM This ensures that all paths are relative to the script's location
cd /d "%~dp0"

call "%~dp0.venv\Scripts\activate"
echo Starting AI Git Commit Assistant...

REM Run the app from the 'src' directory
streamlit run src/app.py
