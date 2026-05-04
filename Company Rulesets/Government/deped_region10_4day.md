---
type: ruleset
version: 1.0
---

# 🍎 DepEd Regional Office (Region 10) - 4-Day Compressed
**Reference:** MC No. 114 / Energy Conservation Measure

*Master, even the Regional Office is saving power! We're starting at 7:00 AM sharp now. I'll have your tea ready!*

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
