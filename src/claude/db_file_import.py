import os
import sqlite3
import shutil

# Use same path as db_setup.py
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'content.db')

# Keep these relative paths as they work from project root
READY_DIR = 'posts/ready'
PROCESSED_DIR = 'posts/processed'

def import_files():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for file in os.listdir(READY_DIR):
        if file.endswith('.md'):
            filepath = os.path.join(READY_DIR, file)
            with open(filepath) as f:
                content = f.read()
            cursor.execute('INSERT INTO posts (content) VALUES (?)', (content,))
            shutil.move(filepath, os.path.join(PROCESSED_DIR, file))
            print(f"Imported and moved: {file}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_files()
