import sqlite3
import os

target_tables = ['ojt_entry', 'attendance', 'entry']
search_root = r'C:\Users\franc\Documents'

print(f"Scanning {search_root} for OJT data...")

for root, dirs, files in os.walk(search_root):
    if 'node_modules' in root or 'venv' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
            db_path = os.path.join(root, file)
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cursor.fetchall()]
                
                for tt in target_tables:
                    if tt in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {tt}")
                        count = cursor.fetchone()[0]
                        print(f"FOUND DB: {db_path}")
                        print(f"  Table '{tt}' has {count} rows.")
                conn.close()
            except:
                pass
