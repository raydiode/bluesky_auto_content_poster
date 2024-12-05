# src/main.py
import signal
import sys
import time
import sqlite3
from datetime import datetime
from post_manager import PostManager
from bluesky_poster import BlueskyPoster, BlueskyCredentials
from db_setup import setup_database
from config import (
    DB_PATH, READY_DIR, PROCESSED_DIR,
    BLUESKY_USERNAME, BLUESKY_PASSWORD,
    TEST_MODE, get_posting_interval, POSTS_PER_RUN
)

def reset_test_posts():
    """Reset all posts back to 'ready' status"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET status = 'ready', 
                posted_at = NULL 
            WHERE status = 'posted'
        ''')
        conn.commit()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal. Finishing current tasks...")
    if TEST_MODE:
        print("Resetting posts to 'ready' status...")
        reset_test_posts()
    sys.exit(0)

def format_status_display(queue_status):
    """Creates a formatted string showing current queue statistics"""
    lines = ["Current Queue Status:"]
    lines.append("-" * 30)
    for status, count in queue_status:
        lines.append(f"{status.title()}: {count} posts")
    lines.append("-" * 30)
    return "\n".join(lines)

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

    try:
        while True:
            # Check for and import new files
            imported_count = post_manager.import_new_files()
            if imported_count:
                print(f"\nImported {imported_count} new files")

            # Process posts up to the configured limit
            posts_processed = 0
            for _ in range(POSTS_PER_RUN):
                post = post_manager.get_next_ready_post()
                if not post:
                    break

                # Process the post
                print(f"\nProcessing Post ID: {post.id}")
                print("-" * 50)
                
                success, message = bluesky.post_content(post.content)
                if not TEST_MODE:
                    status = "posted" if success else "failed"
                    post_manager.update_post_status(
                        post_id=post.id,
                        status=status,
                        posted_at=datetime.now() if success else None
                    )

                print(message)
                posts_processed += 1

            # Show processing summary
            if posts_processed:
                print(f"\nProcessed {posts_processed} posts this run")

            # Display current queue status
            print("\n" + format_status_display(post_manager.get_queue_status()))

            # Wait for next processing cycle
            print(f"\nWaiting {posting_interval} seconds before next run...")
            time.sleep(posting_interval)

    except KeyboardInterrupt:
        if TEST_MODE:
            print("\nResetting posts to 'ready' status...")
            reset_test_posts()
        print("\nShutting down gracefully...")

if __name__ == "__main__":
    main()
