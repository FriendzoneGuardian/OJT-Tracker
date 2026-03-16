# FriendzoneGuardian OJT-Tracker:
# v1.5.0 "Heat of the Moment" Walkthrough 🎨🧬

This document showcases the key features and implementation details of the OJT-Tracker.

## 🚀 Key Features

### 📅 Smart Holiday Tracker (Refined)
The Holiday Tracker has been moved to a dedicated, high-focus modal that is clean and professional.

- **70% Layout**: The modal is now sized at 70% of the viewport, providing a focused view without being overwhelming.
- **7-Item Pagination**: Managed dates are organized into easy-to-navigate pages of 7 items each for optimal UI performance.
- **Auto-Cleanup**: The system automatically deletes holidays and exclusions once they have passed, ensuring a fresh list at all times.

### 🛞 "On Wheels" Deployment
The project is now fully portable!
- **Standalone EXE**: IT staff can build a standalone executable using `bundle_app.py`.
- **One-Click Launch**: The `run.bat` allows for immediate execution without complex environment setup.

### 📊 Fluid Dashboard Layout
- **Log Table Priority**: Daily logs are now positioned at the top for faster data entry.
- **Compact Analytics**: Real-time charts have been optimized to fit seamlessly into the dashboard.

## 🛠️ Implementation Details

### GitHub Repository
The project is officially hosted and version-controlled. Versioning (v1.1.0) is integrated into both the backend and frontend UI.

### Portable Data Storage
Data (SQLite database and logs) is stored in a dedicated `data/` directory relative to the application, making it independent of any specific machine setup.

### Dual Licensing
Ensures compliance through a standard MIT license while maintaining project personality with the "About Time" Public License.
