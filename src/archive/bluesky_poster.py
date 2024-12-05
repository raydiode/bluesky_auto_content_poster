# src/bluesky_poster.py
from dataclasses import dataclass
from typing import Tuple
from atproto import Client

@dataclass
class BlueskyCredentials:
    """Data structure for Bluesky authentication"""
    username: str
    password: str

class BlueskyPoster:
    def __init__(self, credentials: BlueskyCredentials, test_mode: bool = False):
        self.credentials = credentials
        self.test_mode = test_mode
        self._client = None

    def _ensure_client(self):
        """Ensure we have an authenticated client"""
        if not self._client:
            self._client = Client()
            self._client.login(self.credentials.username, self.credentials.password)

    def post_content(self, content: str) -> Tuple[bool, str]:
        """Post content to Bluesky or simulate posting in test mode"""
        if self.test_mode:
            return True, f"Test mode - Would post: {content[:100]}..."

        try:
            self._ensure_client()
            response = self._client.post(text=content)
            return True, "Posted successfully"
        except Exception as e:
            return False, str(e)
# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Validate and set up project paths
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT'))
if not PROJECT_ROOT:
    raise ValueError("PROJECT_ROOT must be set in .env file")

# Directory structure
POSTS_DIR = PROJECT_ROOT / "posts"
DB_DIR = PROJECT_ROOT / "database"
DRAFTS_DIR = POSTS_DIR / "drafts"
READY_DIR = POSTS_DIR / "ready"
PROCESSED_DIR = POSTS_DIR / "processed"
DB_PATH = DB_DIR / "content.db"

# Required directories for the application
REQUIRED_DIRS = [POSTS_DIR, DB_DIR, DRAFTS_DIR, READY_DIR, PROCESSED_DIR]

# Bluesky configuration
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')

# Runtime configuration
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'
TEST_INTERVAL = int(os.getenv('TEST_INTERVAL'))
PRODUCTION_INTERVAL = int(os.getenv('PRODUCTION_INTERVAL'))
POSTS_PER_RUN = int(os.getenv('POSTS_PER_RUN'))

def get_posting_interval():
    """Returns the appropriate posting interval based on the current mode"""
    return TEST_INTERVAL if TEST_MODE else PRODUCTION_INTERVAL
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
# src/main.py
import signal
import sys
import time
from datetime import datetime
from post_manager import PostManager
from bluesky_poster import BlueskyPoster, BlueskyCredentials
from db_setup import setup_database
from config import (
    DB_PATH, READY_DIR, PROCESSED_DIR,
    BLUESKY_USERNAME, BLUESKY_PASSWORD,
    TEST_MODE, get_posting_interval, POSTS_PER_RUN
)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal. Finishing current tasks...")
    sys.exit(0)

def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize the database and required directories
    setup_database()

    # Initialize the post manager and poster
    post_manager = PostManager(
        db_path=DB_PATH,
        ready_dir=READY_DIR,
        processed_dir=PROCESSED_DIR
    )

    bluesky = BlueskyPoster(
        credentials=BlueskyCredentials(
            username=BLUESKY_USERNAME,
            password=BLUESKY_PASSWORD
        ),
        test_mode=TEST_MODE
    )

    # Get the appropriate posting interval
    posting_interval = get_posting_interval()

    print(f"Running in {'TEST' if TEST_MODE else 'PRODUCTION'} mode")
    print(f"Post interval: {posting_interval} seconds")
    print(f"Posts per run: {POSTS_PER_RUN}")

    while True:
        # Check for and import new files
        imported_count = post_manager.import_new_files()
        if imported_count:
            print(f"Imported {imported_count} new files")

        # Process posts up to the configured limit
        posts_processed = 0
        for _ in range(POSTS_PER_RUN):
            post = post_manager.get_next_ready_post()
            if not post:
                break

            success, message = bluesky.post_content(post.content)
            status = "posted" if success else "failed"
            post_manager.update_post_status(
                post_id=post.id,
                status=status,
                posted_at=datetime.now() if success else None
            )

            posts_processed += 1
            print(f"Processed post {post.id}: {status} - {message}")

        if posts_processed:
            print(f"\nProcessed {posts_processed} posts")

        # Show current queue status
        print("\nCurrent queue status:")
        for status, count in post_manager.get_queue_status():
            print(f"{status}: {count}")

        print(f"\nWaiting {posting_interval} seconds before next run...")
        time.sleep(posting_interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
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
