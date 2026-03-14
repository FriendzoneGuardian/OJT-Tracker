# 🛞 Deployment Guide ("On Wheels")

The OJT-Tracker follows the **"On Wheels" philosophy**: it should be portable, self-contained, and require zero system-wide installation once bundled.

## 📦 Running the Standalone EXE
If you received the `FriendzoneGuardian-OJT-Tracker-v1.2.0.exe`:
1. Simply double-click to run.
2. It will create a `data/` folder in the same directory.
3. **Important**: Your database and charts are stored in that `data/` folder. Keep the EXE and the Folder together if you move machines!

## ⚡ One-Click Startup (Python Users)
If you have Python installed but want speed:
- Run `run.bat`. It automatically activates the virtual environment and starts the server.

## 🏗️ How to Bundle (For IT Staff)
To create a new executable:
1. Ensure you have `PyInstaller` installed in your venv.
2. Run `python bundle_app.py`.
3. Check the `dist/` folder for your single-file executable.
