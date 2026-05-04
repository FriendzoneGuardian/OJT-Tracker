---
type: ruleset
version: 1.0
---

# 🌲 DENR CENRO - Pangantucan (4-Day Compressed)
**Reference:** MC No. 114 / Energy Conservation Measure

*Master, the forest office is now on a 10-hour daily shift! Let's make sure we track those early 7:00 AM starts correctly!*

---

## 🕒 1. Official Shift Schedule
- **Morning Shift:** 07:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 06:00 PM

## ⚖️ 2. Transmutation Rules
- **Penalty Logic:** 30 minutes deduction for every 15 minutes of lateness or undertime.

---

## ⚙️ Technical Configuration Block
```json
{
  "grace_period_minutes": 0,
  "morning_start": "07:00",
  "morning_end": "12:00",
  "afternoon_start": "13:00",
  "afternoon_end": "18:00",
  "penalty_per_15_mins_minutes": 30
}
```
