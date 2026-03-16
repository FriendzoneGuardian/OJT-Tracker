# 🤖 Agent Instructions: Guidelines for "Vibecoders"

Welcome, fellow Agent! This document contains specific instructions for AI coding assistants working on the **OJT-Tracker** codebase. Adhering to these rules ensures consistency and prevents "temporal paradoxes" in our logic.

## 🛠️ Tech Stack & Patterns
- **Backend**: Flask + SQLAlchemy. Keep logic in `app.py`.
- **Database**: SQLite. All data must reside in the relative `data/` directory for portability.
- **Frontend**: Vanilla JS + Tailwind CSS (via CDN). Avoid adding heavy frontend frameworks.
- **Iconography**: Use `Lucide-JS`. Run `lucide.createIcons()` after dynamic DOM updates.

## 📏 Coding Standards
1.  **Versioning**: Always reference the `VERSION` constant in `app.py`. If you update features, increment the version (Semantic Versioning).
2.  **Trajectory Logic**: The core value-prop is the "Expected End" date. If you modify how hours are calculated, ensure you account for:
    -   User-defined working days (Saturdays/Sundays are toggleable in Settings)
    -   National Holidays (from `Holiday` model)
    -   User Exclusions (from `ExcludedDate` model)
3.  **Portability**: Never hardcode absolute paths. Use `os.path.join(BASE_DIR, ...)` to ensure it runs "On Wheels".
4.  **Auto-Cleanup**: Maintain the `cleanup_past_dates()` function triggered on startup. It keeps the database lean.
5.  **Clockwork Logic (v1.6.0)**:
    -   **Time-Walk Detection**: Use the `is_night_shift` flag for overnight calculations to handle midnight crossovers.
    -   **Auto-Normalization**: In standard modes, assume afternoon hours (1-9) are PM (13-21). Bypassed in Night Mode.
    -   **Ghost Buffer**: In `get_stats`, we use a `0.001` reduction (`hours_rem = left - 0.001`) to prevent floating-point "ghost days" where the tracker thinks 1 minute remains on a new day.

## 🎨 UI/UX Guidelines
- **Dark Mode First**: The theme is AMOLED Black (`bg-zinc-950`).
- **PAGINATION**: The Holiday modal is limited to **7 items per page**. Do not increase this without a UI redesign request.
- **Animations**: Use Tailwind's `animate-in` utilities for smooth transitions.

## ⚖️ Puns are Mandatory
Every major feature or commit **must** contain at least one time-related pun in the documentation or commit message. This is a licensed requirement under the ATPL.

---
*Good luck, Agent. Make sure you don't run out of tokens!*
