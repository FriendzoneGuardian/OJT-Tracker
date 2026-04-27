# 🕰️ OJT-Tracker v1.8.0 "Chart Surgeon"

Welcome to the **OJT-Tracker**, the only app that understands that _time flies when you're having fun_, but it _crawls when you're rendering 486 hours_.

> "I surgically removed Seaborn and replaced it with Chart.js. The patient is doing fine. It's actually faster now." — v1.8.0 Changelog

## 🚀 Features (That don't slack off)

- **Clockwork Engine**: Refactored logic for Night Owl shifts, Time-Walk crossovers, and Phantom Time fixes.
- **Auto-Normalization**: Type `1:00` in Afternoon fields and it magically becomes `13:00` (Intelligently disabled for Night Owls).
- **Projection Calibration**: Switch between Rolling Average and Manual Speed (hrs/day) strategies in Settings.
- **Overtime Architecture**: Global toggle to allow uncapped daily hours or stick to the standard 8.0h cap.
- **Auto-Sync Holidays (v1.7.0)**: Built-in Selenium scraper to automatically fetch current Philippine holidays from the web.
- **Year-End Sweep (v1.7.1)**: On December 31st, the app will offer a one-click sweep to clean up past holidays and prepare your calendar for the new year!
- **Holiday Integrity (v1.7.3)**: Hotfixed date parsing (supports `D MMM` formats) and manual addition logic to ensure zero-loss temporal tracking.
- **Temporal Archives**: Create database snapshots and merge history from legacy .db, CSV, or XLS files!
- **Chart.js Analytics (v1.8.0)** ✨: 4 interactive chart views — Area, Progress Tracker (Combo), Monthly Breakdown, and Heatmap — rendered client-side with full hover tooltips.
- **Thermal Printing (v1.8.0)** 🖨️: Print an official OJT Proof Log on any Epson TM-82X (or Generic/Text printer). Includes monthly breakers, H:MM formatting, and a fun RPG Level Summary.
- **User Profile (v1.8.0)**: Add your intern name in Settings; it prints on your receipt header.

## 🛠️ Installation (It's about time you did this)

1. **Clone the repo**:
   ```bash
   git clone https://github.com/FriendzoneGuardian/OJT-Tracker.git
   ```
2. **Setup Environment (Mise en Place)**:
   ```bash
   cd OJT-Tracker
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   npm install
   ```
3. **Run the app**:
   ```bash
   npm start
   ```

## ⚡ Bootstrap Matrix (Startup Methods)

| Method | Plan | Context | Command |
| :--- | :--- | :--- | :--- |
| **A: Primary** | **Automated** | Native Desktop App | `npm start` |
| **B: PowerShell** | **Manual Venv** | Terminal-First | `.\venv\Scripts\Activate.ps1; npm start` |
| **C: Standalone** | **Solo-Python** | Pre-v1.3 Legacy | `venv\Scripts\activate; python app.py` |

> [!TIP]
> **Plan B (PowerShell)**: If your shell blocks scripts, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first.
> **Plan C (Standalone)**: Use this if you don't need the Electron shell and prefer access via `http://localhost:8080` in your browser.

## 🖨️ Thermal Printing

Print an official proof of your OJT on any Epson TM-82X or Generic/Text printer:

```bash
python print_time_summary.py
```

See the full [Thermal Printing Guide](Docs/Wiki/Thermal-Printing.md) for layout details and configuration.

## 📊 Analytics

Four interactive chart views replace the old Seaborn-generated images. See the [Analytics & Charts Guide](Docs/Wiki/Analytics-Charts.md).

## 📚 Documentation

- [Thermal Printing Guide](Docs/Wiki/Thermal-Printing.md)
- [Analytics & Charts Guide](Docs/Wiki/Analytics-Charts.md)
- [Release Notes v1.8.0](Docs/release_notes_v1.8.0.md)
- [Agent Instructions](Docs/AgentInstructions.md) *(for AI agents)*
- [Agent Context](Docs/AgentContext.md)

## 🤝 Project Support

Brought to you by **FriendzoneGuardian**. We're here to make sure your OJT journey is **smooth sailing** (or at least better than a leaky canoe).

## 📜 License

This project is licensed under the **"Grandfather Clock"** License: If you use it, you have to tell at least one bad time pun per day.

---

_OJT-Tracker: Helping you track your hours so you don't end up **out of time**._
