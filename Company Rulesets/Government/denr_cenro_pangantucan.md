---
type: ruleset
version: 1.0
---

# 🌲 DENR CENRO - Pangantucan
**Office Address:** Vismin Village, Poblacion, Pangantucan, Bukidnon
**Agency:** Department of Environment and Natural Resources

*Master, here are the rules for the forest protectors! We must keep the schedule as clean as the environment!*

---

## 🕒 1. Official Shift Schedule
- **Morning Shift:** 08:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 05:00 PM

## ⚖️ 2. Transmutation Rules
*As per government standard, we use 15-minute increments for penalty calculations.*

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
