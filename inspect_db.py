import sqlite3
import os

paths = ['ojt_tracker.db', 'instance/ojt_tracker.db']

for db_path in paths:
    abs_path = os.path.abspath(db_path)
    print(f"\n--- Checking: {abs_path} ---")
    if not os.path.exists(db_path):
        print("NOT FOUND")
        continue

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    for table in tables:
        t_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
        count = cursor.fetchone()[0]
        print(f"Table '{t_name}' count: {count}")
    conn.close()
