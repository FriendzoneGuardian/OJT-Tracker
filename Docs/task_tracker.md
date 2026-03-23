# OJT-Tracker Development: v1.0.0 - v1.5.0 "Heat of the Moment"

This document tracks the progress of the OJT-Tracker development.

## Project Phases

### Phase 1: Foundation & Versioning [COMPLETED]
- [x] Create repository structure
- [x] Implement Versioning (v1.1.0)
- [x] Configure portable data handling (`data/` directory)
- [x] Set up local Git repository and initial push

### Phase 2: Holiday Tracking & Trajectory [COMPLETED]
- [x] Implement `Holiday` and `ExcludedDate` models
- [x] Build smart trajectory projection logic
- [x] Create Calendar modal with 70% viewport size
- [x] Implement 7-item pagination for managed dates
- [x] Add auto-cleanup for past dates

### Phase 3: UI & UX Refinement [COMPLETED]
- [x] Swap log table and analytics chart positions
- [x] Shrink and optimize chart components
- [x] Implement AMOELD Dark Mode and responsive layout

### Phase 4: Portability & Deployment [COMPLETED]
- [x] Create legitimate and humorous licenses
- [x] Build `bundle_app.py` for standalone EXE creation
- [x] Create one-click `run.bat` launcher

### Phase 6: Weekend Toggle Implementation [COMPLETED]
- [x] Add `include_saturday/sunday` to `Settings` model
- [x] Update `app.py` trajectory logic
- [x] Add toggles to Settings UI
- [x] Update README with `venv` activation steps
- [x] Final Git Push

### Phase 7: Project Debloat (v1.3.1) [COMPLETED]
- [x] Remove legacy PyInstaller scripts and obsolete launchers
- [x] Delete redundant `instance/` and `license/` folders
- [x] Streamline repository structure for Sidecar deployment

### Phase 8: Electron native Shell (v1.3.0) [COMPLETED]
- [x] Initialize Electron environment (`package.json`, `main.js`)
- [x] Implement Sidecar Architecture (Electron spawns Flask)
- [x] Standardize on AMOLED Dark Mode
- [x] Stress Test: "Shift Storm" UI Refinements (Search/Modals)

### Phase 9: Temporal Archives (v1.4.0) [COMPLETED]
- [x] v1.3.2 Connection Hotfix (127.0.0.1 standardized + Retry Loop)
- [x] Multi-Format Export (Excel, CSV, TXT)
- [x] Database Snapshotting (Automated Backups)
- [x] Import Wizard (History Merging for DB/CSV/XLS)

### Phase 10: Final Polish & Roadmap Sync [COMPLETED]
- [x] Update all docs to v1.4.0
- [x] Backfill Project History (v1.0 - v1.3) ✅
- [x] Tag and Release `v1.4.0` ✅
- [x] Sync Main Repo and Wiki ✅

### Phase 11: Holiday Integrity (v1.6.10) [COMPLETED]
- [x] Remove destructive `cleanup_past_dates` logic
- [x] Implement "Legacy Preservation" for historical holiday data
- [x] Increment version to v1.6.10 🕰️

## Roadmap Summary
| Version | Codename | Key Feature |
|---------|----------|-------------|
| v1.1.0 | Foundation | Portable Data & SQL logic |
| v1.2.0 | Trajectory | Smart Calendar & Predictions |
| v1.3.0 | Shell-Shocked | Electron Desktop Shell |
| v1.4.0 | Temporal Archives | Snapshots & Import Wizard |
| v1.5.0 | Visual & Aesthetics | Intensity Heatmaps & AMOLED Fixes |
| v1.6.0 | Clockwork Calibration | Night Owl mode & Normalization |
| v1.6.10| Legacy preservation | Post-hoc Holiday consistency |
| v1.7.0 | Time Scavenger | Selenium-based automatic Philippine Holiday Scraper |
| v1.7.3 | Holiday Integrity | Hotfixed Scraper date parsing and manual addition logic |
| Future | Phase 13+ | Import Holidays Function, Hardware Integration, Advanced Automation |
