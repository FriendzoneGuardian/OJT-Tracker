# OJT-Tracker Technical Documentation

## Overview
The OJT-Tracker is a Flask-based web application designed to help interns and students track their On-the-Job Training (OJT) hours. It features a robust backend using SQLAlchemy and a modern, responsive frontend built with Tailwind CSS.

## Architecture

### Backend (Python/Flask)
- **Framework**: Flask 3.0.x
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Models**:
    - `OJTEntry`: Stores daily logs (date, morning in/out, afternoon in/out, total hours).
    - `Settings`: Stores application-wide configurations like `target_hours`.
    - `Holiday`: Stores national holidays or official non-working days.
    - `ExcludedDate`: Stores user-defined exclusions (personal days, etc.).
- **Key Libraries**:
    - `pandas` & `xlsxwriter`: Used for generating Excel exports.
    - `matplotlib` & `seaborn`: Used for generating progress charts.

### Frontend (HTML/JS/CSS)
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
- `GET /api/chart`: Returns a base64 encoded PNG of the progress chart.

### Settings, Holidays & Export
- `GET /api/settings`: Fetch current configuration (e.g., target hours).
- `POST /api/settings`: Update configuration.
- `GET /api/holidays`: Fetch all registered holidays.
- `POST /api/holidays`: Add a new holiday.
- `DELETE /api/holidays/<id>`: Remove a holiday.
- `GET /api/exclusions`: Fetch all custom exclusions.
- `POST /api/exclusions`: Add a new exclusion.
- `DELETE /api/exclusions/<id>`: Remove an exclusion.
- `GET /api/export`: Downloads the entire log as an `.xlsx` file.

## Setup & Development

1. **Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install flask flask-sqlalchemy pandas xlsxwriter matplotlib seaborn
   ```

2. **Database Initialization**:
   The database (`ojt_tracker.db`) is automatically created in the `instance/` folder upon the first run of the application.

3. **Running**:
   ```bash
   python app.py
   ```
   The application defaults to `http://localhost:8080`.

## Implementation Notes
- **Smart Trajectory Calculation**: The system projects the completion date by iteratively skipping weekends, national holidays, and user-defined exclusions.
- **Auto-Cleanup**: On application startup, the system automatically removes `Holiday` and `ExcludedDate` records that are in the past.
- **Pagination**: The Holiday Tracker UI implements client-side pagination (7 items per page) for optimal performance and readability.
- **Rendering Fix**: Ensure the `settings-modal` and `calendar-modal` HTML are present in `index.html` to avoid JavaScript initialization errors.
