# src/post_manager.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
import shutil
from typing import Optional, List

@dataclass
class Post:
    """Data structure representing a post"""
    id: Optional[int]
    content: str
    created_at: datetime
    posted_at: Optional[datetime]
    status: str
    filename: Optional[str] = None

class PostManager:
    def __init__(self, db_path: Path, ready_dir: Path, processed_dir: Path):
        self.db_path = db_path
        self.ready_dir = ready_dir
        self.processed_dir = processed_dir
    
    def _get_db_connection(self):
        """Create a database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def import_new_files(self) -> int:
        """Import new markdown files from ready directory into database"""
        imported_count = 0
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            for file in self.ready_dir.glob("*.md"):
                content = file.read_text(encoding='utf-8')
                cursor.execute(
                    'INSERT INTO posts (content, created_at, status) VALUES (?, ?, ?)',
                    (content, datetime.now(), 'ready')
                )
                shutil.move(str(file), str(self.processed_dir / file.name))
                imported_count += 1
        
        return imported_count

    def get_next_ready_post(self) -> Optional[Post]:
        """Retrieve the next post ready for processing"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, content, created_at, posted_at, status
                FROM posts
                WHERE status = 'ready'
                ORDER BY created_at
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return Post(
                    id=row['id'],
                    content=row['content'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    posted_at=datetime.fromisoformat(row['posted_at']) if row['posted_at'] else None,
                    status=row['status']
                )
        return None

    def update_post_status(self, post_id: int, status: str, posted_at: Optional[datetime] = None):
        """Update the status and posting time of a processed post"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE posts
                SET status = ?, posted_at = ?
                WHERE id = ?
            ''', (status, posted_at, post_id))

    def get_queue_status(self) -> List[tuple]:
        """Get the current status counts of all posts"""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM posts
                GROUP BY status
            ''')
            return cursor.fetchall()
