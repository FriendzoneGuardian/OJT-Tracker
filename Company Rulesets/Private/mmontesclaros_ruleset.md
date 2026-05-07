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
> "Update the company policy: Official hours are 7:30 AM to 12:00 PM and 1:00 PM to 4:30 PM. The Official Late Rule is: Any instance of lateness incurs an automatic 1-hour additional deduction, regardless of time or undertimes. This replaces the previous incremental 'Adding Lates' system which only applies to paid employees."

## 1. Official Shift Schedule
- **Morning Shift:** 07:30 AM – 12:00 PM
- **Lunch Break:** 12:00 PM – 01:00 PM
- **Afternoon Shift:** 01:00 PM – 04:30 PM

## 2. Official Late Rule (Transmutation)
This is the current official rule for lateness:
- **Late Penalty:** Any instance of lateness incurs an automatic **1 Hour (60 mins)** additional deduction, regardless of the actual duration or any undertimes.

## 3. Archived/Inactive Rules (Reference Only)
*The following rules are no longer active for the current OJT batch but are preserved for historical context:*

*   **Old Compounding Rule (Tiered):**
    *   1 to 15 minutes: 1 Hour (60 mins) deduction.
    *   16 to 30 minutes: 2 Hours (120 mins) deduction.
    *   *...and so on (1 hour added for every additional 15 minutes).*
    *   *Note: This rule now only applies to paid employees.*
*   **Original 2-Hour Rule:**
    *   If lateness reaches **2 Hours (120 mins)**, an additional **1/2 Day (4 Hours / 240 mins)** deduction is applied.

---

## Technical Configuration Block
*The following JSON block is automatically parsed by the OJT-Tracker to calculate deductions.*

```json
{
  "grace_period_minutes": 15,
  "morning_start": "07:30",
  "morning_end": "12:00",
  "afternoon_start": "13:00",
  "afternoon_end": "16:30",
  "penalty_per_15_mins_minutes": 0,
  "fixed_late_penalty_minutes": 60,
  "fixed_daily_deduction_minutes": 0,
  "include_saturday": true,
  "_inactive_compounding_penalty_rate": 60,
  "_inactive_2hr_half_day_penalty_minutes": 240
}
```
