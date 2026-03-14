@echo off
echo 🕰️ Starting OJT-Tracker (Portable Mode)...
if not exist venv (
    echo 📦 Setting up portable environment...
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
)
echo 🚀 Launching...
start http://localhost:8080
venv\Scripts\python app.py
pause
