# src/db_setup.py
import sqlite3
from config import DB_PATH, REQUIRED_DIRS

def setup_directories():
    """Create all required directories if they don't exist"""
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

def setup_database():
    """Initialize the SQLite database with required schema"""
    setup_directories()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        posted_at TIMESTAMP,
        status TEXT CHECK(status IN ('ready', 'posted', 'failed')) NOT NULL DEFAULT 'ready'
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database setup complete at: {DB_PATH}")
