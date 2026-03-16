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
2. **Enter the directory**:
   ```bash
   cd OJT-Tracker
   ```
3. **Setup Backend (Python)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Setup Frontend (Electron)**:
   ```bash
   npm install
   ```
5. **Run the app**:
   ```bash
   npm start
   ```
   _(Running `npm start` automatically handles the Flask backend for you!)_
6. **Read the Docs & Wiki**: Check out our [GitHub Wiki](https://github.com/FriendzoneGuardian/OJT-Tracker/wiki) or the [Docs/](Docs/) folder for technical details!
7. **Shift Storm**: [READ THE SETUP ORDEAL GUIDE](https://github.com/FriendzoneGuardian/OJT-Tracker/wiki/Shift-Storm).
8. **Spicy FAQ**: [SHIFT STORM FAQ](https://github.com/FriendzoneGuardian/OJT-Tracker/wiki/Shift-Storm-FAQ) (Warning: Selective Language).

## ⚡ Quick Start (Re-running the app)

If you've already installed the app and just want to start it again:

1. Open your terminal in the `OJT-Tracker` folder.
2. Run the magic command:

   ```bash
   # Windows
   venv\Scripts\activate && python app.py

   # Mac/Linux
   source venv/bin/activate && python app.py
   ```

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
