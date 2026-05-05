---
type: ruleset
version: 1.1
---

# M. Montesclaros Group (Montesclaros Group of Companies)
**Head Office:** Patag, Bagontaas, Valencia City, Bukidnon, Philippines
**Parent Company:** M. Montesclaros Holdings, Inc. (MMHI)

## Covered Entities & Industries:
*   **M. Montesclaros Enterprises, Inc. (MMEI)** – General Engineering & Construction
*   **M. Montesclaros Farms, Inc. (MMFI)** – Livestock & Agricultural Production
*   **M. Montesclaros Hospitality Corp. (MMHC)** – Hotels (Double M Hotel) & Dining (Roadhouse Café)
*   **Montesclaros Development Corp. (MMDC)** – Real Estate & Property Development

**Opening Prompt:**
> "Update the company policy: Official hours are 7:30 AM to 12:00 PM and 1:00 PM to 4:30 PM. Penalties for late arrival or undertime are: 1 hour deduction for the first 1-15 minutes, and an additional 1 hour deduction for every succeeding 15 minutes. This applies to both morning and afternoon shifts."

## 1. Official Shift Schedule
- **Morning Shift:** 07:30 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 04:30 PM

## 2. Late & Undertime Penalty (Transmutation)
Any instance of late arrival or early departure (undertime) is penalized in 15-minute increments:
- **1 to 15 minutes:** 1 Hour (60 mins) deduction.
- **16 to 30 minutes:** 2 Hours (120 mins) deduction.
- **31 to 45 minutes:** 3 Hours (180 mins) deduction.
- **46 to 60 minutes:** 4 Hours (240 mins) deduction.
- *...and so on (1 hour added for every additional 15 minutes).*

---

## Technical Configuration Block
*The following JSON block is automatically parsed by the OJT-Tracker to calculate deductions.*

```json
{
  "grace_period_minutes": 15,
  "morning_start": "08:00",
  "morning_end": "12:00",
  "afternoon_start": "13:00",
  "afternoon_end": "16:00",
  "penalty_per_15_mins_minutes": 60,
  "fixed_daily_deduction_minutes": 0,
  "include_saturday": true
}
```
