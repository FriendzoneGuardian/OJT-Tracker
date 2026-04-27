# 📊 Analytics & Charts

OJT-Tracker v1.8.0 replaces the server-side Seaborn/Matplotlib charting stack with **Chart.js** — rendering entirely in the browser with full interactivity and no Python charting dependencies.

---

## Chart Views

The chart panel appears below the OJT stats cards. Use the **"Next View →"** button (top-right of the chart card) to cycle through all 4 views. Your preferred view is saved in `localStorage`.

### View 1 — Area Chart *(Default)*
> `Daily Hours (Area)`

A smooth line chart with scarlet area fill showing your daily rendered hours over the last 90 days. Best for spotting momentum and consistency gaps at a glance.

- **X-axis**: Date labels (MM-DD)
- **Y-axis**: Hours (0–max)
- **Tooltip**: Exact hours on hover

### View 2 — Progress Tracker
> `Progress Tracker`

A dual-axis combo chart:
- **Scarlet bars** = daily hours (left Y-axis)
- **Amber line** = cumulative hours total (right Y-axis)
- **Dashed grey line** = your target (e.g., 486h)

Best for answering "am I on pace?" without calculating anything.

### View 3 — Monthly Breakdown
> `Monthly Breakdown`

A horizontal bar chart grouped by calendar month showing total hours rendered per month. Ideal for presentations, reviews, or proof-of-OJT documentation.

- Labels auto-generated from your actual entry data (e.g., `Feb 2026`, `Mar 2026`)
- Color intensity shifts per month

### View 4 — Temporal Intensity (Heatmap)
> `Temporal Intensity`

A custom Canvas2D GitHub-style contribution heatmap showing the last 8 weeks of activity:
- **Rows**: Mon–Sun
- **Columns**: Weekly buckets (oldest → current)
- **Cell color**: Scarlet, intensity-scaled to hours (0 = dark grey, 8h = full scarlet)
- **Dimmed cells** = future dates
- **Hours label** inside each cell if hours > 0

---

## Technical Notes

### Data Endpoint
All chart views share a single API call:
```
GET /api/chart-data?days=90
```

Returns:
```json
{
  "labels": ["04-01", "04-02", ...],
  "hours": [8.0, 7.5, ...],
  "cumulative": [8.0, 15.5, ...],
  "target": 486.0,
  "monthly": {"Apr 2026": 64.5, ...},
  "weekday": {"Mon": 7.8, "Tue": 8.0, ...},
  "heatmap": [[0, 8, 7.5, ...], ...],
  "heatmap_weeks": ["04/07", "04/14", ...]
}
```

### Theme Awareness
All chart colors adapt to the current theme (Light / Dark / AMOLED) automatically when you switch themes — no server call needed.

### Bundled Locally
Chart.js is bundled at `static/js/chart.min.js` (v4.4.3, ~200KB) for 100% offline Electron operation.
