import sqlite3
import os

paths = [
    'ojt_tracker.db',
    'instance/ojt_tracker.db',
    'data/ojt_tracker.db'
]

for p in paths:
    if os.path.exists(p):
        print(f"\n--- {p} ---")
        try:
            conn = sqlite3.connect(p)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                t_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
                count = cursor.fetchone()[0]
                print(f"Table '{t_name}': {count} rows")
                
                # Show some sample data if rows > 0
                if count > 0 and t_name == 'ojt_entry':
                    cursor.execute(f"SELECT * FROM {t_name} LIMIT 3")
                    print(f"  Samples: {cursor.fetchall()}")
            conn.close()
        except Exception as e:
            print(f"Error reading {p}: {e}")
    else:
        print(f"\n--- {p} NOT FOUND ---")
