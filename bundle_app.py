import os
import subprocess
import sys

def build():
    print("🚀 Starting OJT-Tracker 'On Wheels' Build...")
    
    # Ensure dependencies are installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "flask", "flask-sqlalchemy", "pandas", "xlsxwriter", "matplotlib", "seaborn"])
    
    # PyInstaller Command
    # --onefile: Bundle everything into a single EXE (optional, but better for non-devs)
    # --add-data: Include templates, static, and initial holidays
    # --noconsole: Hide the terminal window (optional, IT might prefer a console for logs)
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed", # Remove this if you want IT to see terminal logs
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--name", "OJT-Tracker-v1.1",
        "app.py"
    ]
    
    print(f"📦 Bundling with command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\n✅ Build Complete! Your 'Wheels' are ready in the 'dist/' folder.")
    print("📝 Note: The first run will create a 'data/' folder next to the EXE for your logs.")

if __name__ == "__main__":
    build()
