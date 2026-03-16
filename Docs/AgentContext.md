# 🧠 Agent Context: Project Brain & Soul

This document provides high-level context for AI agents to understand the "Why" behind the **OJT-Tracker**.

## 🌟 Project Purpose
The OJT-Tracker was born out of a need to accurately predict internship completion dates. Most trackers just divide "Hours Left" by "8", but students don't work every day. This app factors in the complexity of life, holidays, and personal time.

## 🏗️ Architectural Decisions

### 1. Relative Data Storage (`data/` folder)
We moved away from instance folders to a root `data/` folder to support "On Wheels" (portable) deployment. This allows IT staff to move the app across machines without reconfiguring environment variables.

### 2. The Iterative Projection Model
The "Expected End" calculation isn't a simple division. It's a "simulated walk" through the calendar. It starts at `today` and steps forward day-by-day, skipping non-working days until the target hours are met. 
- **Strategies (v1.6.0)**: Added `Rolling Average` (14-day history) vs `Manual Speed` (hrs/day override).
- **Configuration**: Saturdays and Sundays can be toggled as working days via the Settings modal.
- **Accuracy**: This approach is computationally slightly more expensive but infinitely more accurate.

### 3. Client-Side Pagination
We use a 7-item limit for the Holiday list. This was a design choice to prevent long-scrolling modals and keep the "Add Entry" form always visible on the left side of the 70% width modal.

## 📈 Current State & Debt
- **v1.6.0**: "Clockwork Calibration" release. Introduces Night Owl mode, Auto-Normalization, and Manual Projections.
- **Known Quirks**: Matplotlib generates charts on the server and sends them as Base64. This is for portability (no need for complex JS charting libs), but it means charts are static until the next fetch.
- **Future Growth**: Looking into multi-user support or cloud-sync, though the current "Offline First" philosophy is a core feature.

## 🤝 Branding
The project is officially supported and branded by **FriendzoneGuardian**. Maintain this tone: helpful, technical, but heavily laden with time-based dad jokes.

---
*Context is king, but timing is everything.*
