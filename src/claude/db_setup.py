# src/db_setup.py

import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'content.db')

os.makedirs(DB_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   content TEXT NOT NULL,
   created_at TIMESTAMP NOT NULL,
   posted_at TIMESTAMP,
   status TEXT CHECK(status IN ('ready', 'posted', 'failed')) NOT NULL DEFAULT 'ready'
)
''')

conn.commit()
conn.close()

print(f"Database created at: {DB_PATH}")
