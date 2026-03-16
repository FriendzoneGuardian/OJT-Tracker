# OJT-Tracker Technical Documentation

## Overview
The OJT-Tracker is a Flask-based web application designed to help interns and students track their On-the-Job Training (OJT) hours. It features a robust backend using SQLAlchemy and a modern, responsive frontend built with Tailwind CSS.

## Architecture

### Backend (Python/Flask) - The Sidecar
- **Framework**: Flask 3.0.x
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Data Path**: `data/ojt_tracker.db` (Portable logic)
- **Models**:
    - `OJTEntry`: Stores daily logs (date, morning in/out, afternoon in/out, total hours).
    - `Settings`: Stores application-wide configurations (target hours, weekend toggles).
    - `Holiday`: Stores national holidays or official non-working days.
    - `ExcludedDate`: Stores user-defined exclusions.

### Frontend (Desktop Shell)
- **Runtime**: Electron
- **Communication**: Inter-Process Communication (IPC) via `main.js`.
- **Styling**: Tailwind CSS for a premium, dark-mode first design.
- **Icons**: Lucide-JS for consistent iconography.
- **Dynamic Updates**: Pure JavaScript (Fetch API) for real-time data rendering without page reloads.

## API Endpoints

### Entries
- `GET /api/entries`: Returns all log entries sorted by date.
- `POST /api/entries`: Create or update an entry.
- `DELETE /api/entries/<id>`: Delete a specific entry.

### Statistics & Analytics
- `GET /api/stats`: Returns calculated metrics including:
    - Total Hours Rendered
    - Remaining Hours
    - Average Hours per Day
    - Expected Completion Date (based on trajectory)
- `GET /api/chart`: Returns a base64 encoded PNG of the progress chart or heatmap.
    - `type`: (`heatmap`, `bar`) - **NEW**. Select visual representation.
    - `theme`: (`light`, `dark`, `amoled`) - Adjust palette based on theme.

### Settings, Holidays & Export
- `GET /api/settings`: Fetch current configuration (e.g., target hours).
- `POST /api/settings`: Update configuration.
- `GET /api/holidays`: Fetch all registered holidays.
- `POST /api/holidays`: Add a new holiday.
- `DELETE /api/holidays/<id>`: Remove a holiday.
- `GET /api/exclusions`: Fetch all custom exclusions.
- `POST /api/exclusions`: Add a new exclusion.
- `DELETE /api/exclusions/<id>`: Remove an exclusion.
- `GET /api/export/multi`: Downloads log in `.xlsx`, `.csv`, or `.txt` formats.
- `POST /api/snapshot`: Creates a timestamped database backup in `data/snapshots/`.
- `GET /api/snapshots`: Lists all available database snapshots.
- `POST /api/import`: Merges history from an uploaded `.db`, `.csv`, or `.xlsx` file.

## Setup & Development (Shell-Shocked)

1. **Python Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Node/Electron**:
   ```bash
   npm install
   ```

3. **Running**:
   ```bash
   npm start
   ```
   The application will launch in its own window. Backend logs are suppressed by default for a clean Vibe.

4. **Building Portable EXE**:
   ```bash
   npm run dist
   ```
   Output will be in the `dist_electron/` folder.

## Implementation Notes
- **Smart Trajectory Calculation**: The system projects the completion date by iteratively skipping weekends, national holidays, and user-defined exclusions.
- **Auto-Cleanup**: On application startup, the system automatically removes `Holiday` and `ExcludedDate` records that are in the past.
- **Pagination**: The Holiday Tracker UI implements client-side pagination (7 items per page).
- **Branding**: Humorous documentation is maintained under the **"Shift Storm"** series on the GitHub Wiki.
