# FriendzoneGuardian OJT-Tracker Implementation Plan

This document outlines the high-level implementation strategies used to build the OJT-Tracker v1.1.0.

## Core Features Implementation

### 📅 Smart Trajectory Projection
The "Expected End" date calculation uses an iterative projection model:
- **Exclusion Logic**: Skips weekends, national holidays, and user-defined exclusions.
- **Dynamic Updates**: Recalculates instantly when log entries or holidays are modified.

### 📅 Smart Holiday Tracker (Refined)
The Holiday Tracker is a dedicated system for managing non-working days:
- **70% Layout**: Optimized modal size for focused calendar management.
- **7-Item Pagination**: Client-side pagination for readability and performance.
- **Auto-Cleanup**: Automatically removes past holidays on startup.

### 📊 UI Layout & Analytics
- **Priority Loading**: Recent log entries are prioritized above the analytics chart.
- **Compact Visuals**: Shrunk Matplotlib/Seaborn charts for better dashboard composition.

### 🛞 "On Wheels" Portability
- **Relative Storage**: Data is stored in a `data/` folder relative to the execution path.
- **Standalone Build**: Support for PyInstaller bundling into a single Windows EXE.

## Verification Workflow
- **Automated**: Browser-based testing for modal interactions and pagination.
- **Manual**: Trajectory accuracy checks and database persistence verification.
