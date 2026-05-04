---
type: ruleset
version: 1.1
---

# 📦 OBX Solutions Technology, Inc.
**Office Address:** Door 3, 3rd Floor, VLC Tower One, Upper Carmen, Cagayan de Oro City
**Industry:** IT Solutions & Software Development

*Master, I've located their office in the VLC Tower! It's right in the heart of Uptown CDO. I've updated the rules so you can be a perfect tech professional!*

---

## 🕒 1. Official Shift Schedule
- **Morning Shift:** 08:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 05:00 PM

## ⚖️ 2. Transmutation Rules
*Master, tech companies usually have strict delivery timelines, so I've kept the high-penalty logic for precision!*

- **Penalty Logic:** 60 minutes (1 hour) deduction for every 15 minutes of lateness or undertime.

---

## ⚙️ Technical Configuration Block
```json
{
  "grace_period_minutes": 0,
  "morning_start": "08:00",
  "morning_end": "12:00",
  "afternoon_start": "13:00",
  "afternoon_end": "17:00",
  "penalty_per_15_mins_minutes": 60
}
```
