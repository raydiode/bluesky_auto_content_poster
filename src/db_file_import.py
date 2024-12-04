import os
import sqlite3
import shutil
from datetime import datetime

# Define paths relative to the script's location
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Project root
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'content.db')

READY_DIR = os.path.join(BASE_DIR, 'posts', 'ready')
PROCESSED_DIR = os.path.join(BASE_DIR, 'posts', 'processed')

def import_files():
    # Ensure the required directories exist
    if not os.path.exists(READY_DIR):
        raise FileNotFoundError(f"Directory not found: {READY_DIR}")
    if not os.path.exists(PROCESSED_DIR):
        raise FileNotFoundError(f"Directory not found: {PROCESSED_DIR}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Iterate through markdown files in the READY_DIR
    for file in os.listdir(READY_DIR):
        if file.endswith('.md'):
            filepath = os.path.join(READY_DIR, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            created_at = datetime.now()
            cursor.execute('INSERT INTO posts (content, created_at) VALUES (?, ?)', (content, created_at))
            shutil.move(filepath, os.path.join(PROCESSED_DIR, file))
            print(f"Imported and moved: {file}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_files()

