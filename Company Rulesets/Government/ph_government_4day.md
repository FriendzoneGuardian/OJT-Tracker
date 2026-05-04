---
type: ruleset
version: 1.0
---

# 🏛️ Philippine Government Offices (4-Day Compressed)
**Reference:** Memorandum Circular No. 114 (2026)
**Reason:** Energy & Fuel Conservation Strategy

*Master, the government has moved to a 4-day schedule to save energy! We'll have to work longer days (10 hours!), but you get a longer weekend! I've adjusted the clocks for you!*

---

## 🕒 1. Official Shift Schedule (Monday – Thursday)
- **Morning Shift:** 07:00 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 06:00 PM
- *Total Working Hours: 10 Hours/Day*

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
