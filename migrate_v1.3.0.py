import sqlite3
import os

db_path = 'data/ojt_tracker.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check Settings table
    cursor.execute("PRAGMA table_info(settings)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'include_saturday' not in columns:
        print("Adding include_saturday to settings...")
        cursor.execute("ALTER TABLE settings ADD COLUMN include_saturday BOOLEAN DEFAULT 0")
        
    if 'include_sunday' not in columns:
        print("Adding include_sunday to settings...")
        cursor.execute("ALTER TABLE settings ADD COLUMN include_sunday BOOLEAN DEFAULT 0")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
