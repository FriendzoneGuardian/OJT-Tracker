## 📋 v1.8.0 "Chart Surgeon" — Release Notes

### Summary

This release performs a major pivot from server-side Python charting (Seaborn/Matplotlib) to client-side Chart.js rendering, adds full thermal printing support for the Epson TM-82X including an official OJT Proof Log, and includes several UI polish fixes across the dashboard.

---

### 🆕 New Features

#### Chart.js Migration (Seaborn → Chart.js)
- **Replaced** the `seaborn`, `matplotlib`, and `base64` stack with a locally-bundled `chart.min.js` (~200KB vs ~150MB of Python deps).
- **New `/api/chart-data` endpoint** returns raw JSON arrays (labels, hours, cumulative, monthly, weekday, heatmap grid) instead of Base64 PNGs.
- **4 Interactive Chart Views** — cycled via the "Next View →" toggle button:
  1. **Area Chart** *(Default)* — Daily hours with scarlet fill
  2. **Progress Tracker** — Dual-axis combo: daily bars + amber cumulative line + dashed 486h target
  3. **Monthly Breakdown** — Horizontal bar chart grouped by month
  4. **Temporal Intensity** — Custom Canvas2D GitHub-style 8-week heatmap with scarlet intensity gradient

#### Thermal Printing — `print_time_summary.py`
- **Proof of OJT Log** — Full entry history printed chronologically (all entries, not just last 5).
- **Monthly Breakers** — `---[APR (4)] -- [64.5h/13d]---` separators with inline stats.
- **H:MM Format** — All hours displayed as `H:MM` instead of decimal.
- **Remaining with Days Left** — `Remaining : 120.5 hrs (15d left)` inline.
- **Avg/Day** shows both decimal and HH:MM: `Avg/Day : 8.2 hrs (8:12)`.
- **Version Header** — `OJT TRACKER - 1.7.3` in the receipt header.
- **RPG-Style Level Summary** — Fun-but-formal footer showing RANK, STATUS (GRINDING/IDLE), and EXP %.

#### User Profile — `user_name` Field
- Added `user_name` VARCHAR column to the `Settings` table with auto-migration.
- Settings modal now includes an "OJT Intern Name" field, printed prominently on the thermal receipt header.

---

### 🔧 Fixes & Improvements

- **Export Dropdown** — Fixed text disappearing in Dark/AMOLED modes. Redesigned with icon containers, wider width, and explicit dark-mode text color.
- **Table Headers** — Upgraded from `gray-500` to `zinc-400` for better dark mode readability.
- **Modal Z-Index** — All modals bumped to `z-[100]` to prevent dashboard header overlap.
- **Fixed `@apply` CSS** — Replaced Tailwind `@apply` in a raw `<style>` tag with standard CSS equivalents (fixes focus ring and input selectability).
- **Settings Name Field** — Resolved selectability issue caused by z-index stacking context conflict.
- **XlsxWriter** — Added `xlsxwriter==3.2.9` to `requirements.txt` for Excel exports.

---

### 🗑️ Removed Dependencies

| Package | Reason |
|---|---|
| `seaborn` | Replaced by Chart.js |
| `matplotlib` | Replaced by Chart.js |
| `base64` | No longer needed for chart rendering |
| `numpy` | Was only used inside the chart route |

**Estimated venv size reduction: ~120–150 MB**

---

### 📦 Files Changed

| File | Change Type |
|---|---|
| `app.py` | Modified — removed chart libs, added `/api/chart-data`, `user_name` migration |
| `templates/index.html` | Modified — Chart.js canvas, 4-view toggle, z-index fixes, dropdown redesign |
| `templates/loading.html` | Modified — new loading quotes, version bump |
| `print_time_summary.py` | Modified — full proof log, H:MM format, level summary |
| `requirements.txt` | Modified — removed seaborn/matplotlib/numpy, added XlsxWriter |
| `static/js/chart.min.js` | Added — locally bundled Chart.js v4.4.3 |
| `Docs/Wiki/` | Added — new wiki pages for features |
| `main.js` | Modified — version string update |
