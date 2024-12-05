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

