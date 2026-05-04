---
type: ruleset
version: 1.0
---

# 🍎 DepEd Regional Office (Region 10)
**Office Address:** Zone 1, Upper Balulang, Cagayan de Oro City
**Agency:** Department of Education - Northern Mindanao

*Master, the teachers and staff here are very punctual! Let's make sure our tracker reflects their high standards!*

---

## 🕒 1. Official Shift Schedule
- **Morning Shift:** 08:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 05:00 PM

## ⚖️ 2. Transmutation Rules
- **Penalty Logic:** 30 minutes deduction for every 15 minutes of lateness or undertime.

---

## ⚙️ Technical Configuration Block
```json
{
  "grace_period_minutes": 0,
  "morning_start": "08:00",
  "morning_end": "12:00",
  "afternoon_start": "13:00",
  "afternoon_end": "17:00",
  "penalty_per_15_mins_minutes": 30
}
```
