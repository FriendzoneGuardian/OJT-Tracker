import sqlite3
import os

db_path = r'C:\Users\franc\Documents\TestPOS-1.0\db.sqlite3'
print(f"Checking DB at: {db_path}")

if not os.path.exists(db_path):
    print("DB file NOT found!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    for table in tables:
        t_name = table[0]
        if 'ojt' in t_name.lower() or 'entry' in t_name.lower():
            cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
            count = cursor.fetchone()[0]
            print(f"FOUND INTERESTING TABLE: '{t_name}' count: {count}")
            
    conn.close()
