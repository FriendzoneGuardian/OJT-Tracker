# Merge Request Ticket: v1.5.0 -> Main 🎫

**From Branch**: `v1.4-temporal-archives` (containing v1.4.0 and v1.5.0 updates)
**To Branch**: `shell-shocked` (Main Archive)
**Priority**: High (Visual Fixes & Legibility)

## Summary of Changes
This request merges the **v1.4.0 "Temporal Archives"** (Backups & Imports) and the **v1.5.0 "Visual & Aesthetics"** (Heatmaps & AMOLED Fixes) into the main production shell.

### 🚀 Milestone Highlights
- **v1.4.0 Foundation**:
    - Implemented `shutil`-based database snapshotting system.
    - Added comprehensive Multi-Format Import Wizard (DB/CSV/XLSX).
    - Hardened loopback communication for Electron stability.
- **v1.5.0 Visual Polish**:
    - Swapped primary dashboard visual for a **Github-style Intensity Heatmap**.
    - Added runtime **Bar Graph / Heatmap Toggle** via frontend API switch.
    - **Hotfixed Readability**: Resolved white-on-white text issues in Dark/AMOLED dropdowns and menus.

## Technical Notes
- **Dependencies**: Added `numpy` for heatmap grid calculations.
- **UI Architecture**: Injected explicit CSS variable overrides for native HTML select/option visibility in AMOLED mode.
- **API Extension**: `/api/chart` now supports `type` and `theme` parameters for dynamic re-rendering.

## Verification Status
- [x] Selenium "Kitchen Nightmares" Stress Tests passed.
- [x] Manual AMOLED readability verification passed.
- [x] Import/Export collision detection verified.

**Requesting Merge and Final Tagging to `v1.5.0-final`.**
