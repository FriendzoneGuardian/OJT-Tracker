---
type: ruleset
version: 1.0
---

# 🏛️ Philippine Government Offices (General)
**Scope:** National Government Agencies (NGAs), LGUs, and GOCCs
**Standard:** Civil Service Commission (CSC) Guidelines

*Master, this ruleset is designed for all official government duty! Whether it's a City Hall or a National Bureau, these rules will keep your OJT record as official as a stamped document!*

---

## 🕒 1. Official Shift Schedule
- **Morning Shift:** 08:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 05:00 PM

## ⚖️ 2. Transmutation Rules
*In public service, every minute belongs to the people! I've set a firm but fair deduction logic for government OJT work.*

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

*I've made sure this template follows the most common government office hours, Master! Service with a smile!* 😊
