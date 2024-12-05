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

    print("\nBluesky Poster System Starting")
    print(f"Mode: {'TEST' if TEST_MODE else 'PRODUCTION'}")
    print(f"Posting Interval: {posting_interval} seconds")
    print(f"Posts Per Run: {POSTS_PER_RUN}")
    print("-" * 50)

    while True:
        # Import new posts
        imported_count = post_manager.import_new_files()
        if imported_count:
            print(f"Imported {imported_count} new posts")

        # Process posts
        for _ in range(POSTS_PER_RUN):
            post = post_manager.get_next_ready_post()
            if not post:
                break

            success, message = bluesky.post_content(post.content)
            status = "posted" if success else "failed"
            post_manager.update_post_status(post_id=post.id, status=status, posted_at=datetime.now() if success else None)

            print(f"Post {post.id}: {message}")

        time.sleep(posting_interval)

if __name__ == "__main__":
    post_manager = None  # Define outside try block for finally access
    try:
        print("\nStarting Bluesky Poster System")
        print(f"Mode: {'TEST' if TEST_MODE else 'PRODUCTION'}")
        post_manager = PostManager(
            db_path=DB_PATH,
            ready_dir=READY_DIR,
            processed_dir=PROCESSED_DIR
        )
        main()
    finally:
        if TEST_MODE and post_manager:
            post_manager.reset_test_mode()
            print("Test mode cleanup completed")
            print("-" * 50)
