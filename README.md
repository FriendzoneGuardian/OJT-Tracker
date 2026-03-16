# 🕰️ OJT-Tracker v1.6.0 "Clockwork Calibration"

Welcome to the **OJT-Tracker**, the only app that understands that _time flies when you're having fun_, but it _crawls when you're rendering 486 hours_.

If you're looking for a way to track your internship hours without losing your mind, you've come to the **right place at the right time**.

## 🕒 Why use OJT-Tracker?

Because manually calculating hours is a **second-rate** experience. We're here to give you a **hand** (specifically the big one and the little one).

> "I told my boss I needed a raise because I was doing the work of three men. He told me to tell the other two to get back to work. I guess I just didn't have the **timing** right."

## 🚀 Features (That don't slack off)

- **Clockwork Engine**: Refactored logic for Night Owl shifts, Time-Walk crossovers, and Phantom Time fixes.
- **Auto-Normalization**: Type `1:00` in Afternoon fields and it magically becomes `13:00` (Intelligently disabled for Night Owls).
- **Projection Calibration**: Switch between Rolling Average and Manual Speed (hrs/day) strategies in Settings.
- **Temporal Heatmaps**: A GitHub-style intensity map showing work density over the last 8 weeks.
- **Overtime Architecture**: Global toggle to allow uncapped daily hours or stick to the standard 8.0h cap.
- **Temporal Archives**: Create database snapshots and merge history from legacy .db, CSV, or XLS files!

## 🛠️ Installation (It's about time you did this)

1. **Clone the repo**:
   ```bash
   git clone https://github.com/FriendzoneGuardian/OJT-Tracker.git
   ```
2. **Setup Environment (Mise en Place)**:
   ```bash
   cd OJT-Tracker
   python -m venv venv
   # Activation is handled automatically by 'npm start' in v1.6.8+
   # But you still need to install the initial dependencies:
   venv\Scripts\activate
   pip install -r requirements.txt
   npm install
   ```
3. **Run the app**:
   ```bash
   npm start
   ```

## ⚡ Bootstrap Matrix (Startup Methods)

If the primary method fails, use the following manual fallback plans:

| Method | Plan | Context | Command |
| :--- | :--- | :--- | :--- |
| **A: Primary** | **Automated** | Native Desktop App | `npm start` |
| **B: PowerShell** | **Manual Venv** | Terminal-First | `.\venv\Scripts\Activate.ps1; npm start` |
| **C: Standalone** | **Solo-Python** | Pre-v1.3 Legacy | `venv\Scripts\activate; python app.py` |

> [!TIP]
> **Plan B (PowerShell)**: If your shell blocks scripts, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first.
> **Plan C (Standalone)**: Use this if you don't need the Electron shell and prefer access via `http://localhost:8080` in your browser.

3. **For Vibecoders**: If you're an AI agent, read our [Agent Instructions](Docs/AgentInstructions.md) and [Agent Context](Docs/AgentContext.md).

## 🤝 Project Support

Brought to you by **FriendzoneGuardian**. We're here to make sure your OJT journey is **smooth sailing** (or at least better than a leaky canoe).

## 💡 Pro-Tip

Don't worry if the app feels slow at first. It just needs a **minute** to get its **gears** turning.

> "Why did the man sit on his clock? He wanted to be **on time**." (Classic, right?)

## 📜 License

This project is licensed under the **"Grandfather Clock"** License: If you use it, you have to tell at least one bad time pun per day.

---

_OJT-Tracker: Helping you track your hours so you don't end up **out of time**._
