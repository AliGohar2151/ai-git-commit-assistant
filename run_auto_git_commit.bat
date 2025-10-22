@echo off
call "%~dp0.venv\Scripts\activate"
cd /d "%~dp0"
echo Starting AI Git Commit Assistant...
streamlit run app.py
pause
