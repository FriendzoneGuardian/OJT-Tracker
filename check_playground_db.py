import sqlite3
import os

db_path = r'C:\Users\franc\.gemini\antigravity\playground\spectral-star\instance\ojt_tracker.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ojt_entry")
    rows = cursor.fetchall()
    print(f"Spectral-Star Playground Entries ({len(rows)}):")
    for r in rows:
        print(r)
    conn.close()
else:
    print("Not found")
