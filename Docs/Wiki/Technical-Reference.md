# 🛠️ Technical Reference (Agent-Friendly)

Welcome, Vibecoders and AI Agents. This project is optimized for AI collaboration.

## 🏗️ Architecture
- **Backend**: Flask + SQLAlchemy (SQLite).
- **Frontend**: Tailwind CSS + Lucide Icons + Vanilla JS (Modern Fetch API).
- **Storage**: Portable `data/` directory at the project root.

## 🤖 AI Agent Guidelines
We maintain specialized documentation to help AI assistants understand the "vibes" and strict logic of the project:
- [Agent Instructions](../AgentInstructions.md): Rules on versioning, trajectory logic, and aesthetics.
- [Agent Context](../AgentContext.md): Rationale behind architectural decisions (Portable storage, recursive projection).

## 🚀 Local Setup
```bash
git clone https://github.com/FriendzoneGuardian/OJT-Tracker.git
cd OJT-Tracker
python -m venv venv
# Windows
venv\Scripts\activate
# Install
pip install -r requirements.txt
# Run
python app.py
```

## 📊 Logic: Projecting the End Date
The logic resides in `app.py` under the `get_stats()` endpoint. It uses an iterative `while` loop that increments `timedelta(days=1)` and validates each day against the `Settings` model's weekend toggles and the `Holiday`/`ExcludedDate` tables.
