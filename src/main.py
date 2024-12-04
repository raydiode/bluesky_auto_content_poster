import os
import sys

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.db_setup import DB_PATH
from src.folder_check import check_folders
from src.db_file_import import import_files
from src.post_to_bluesky import process_ready_post

def main():
    # Step 1: Check if the database exists, run setup only if needed
    if not os.path.exists(DB_PATH):
        print("Database not found. Running setup...")
        from src.db_setup import conn  # This will trigger db_setup.py
        conn.close()
    else:
        print("Database already set up.")

    # Step 2: Verify required folders exist and report their status
    print("\nChecking folders...")
    check_folders()

    # Step 3: Import markdown files from 'ready' to the database
    print("\nImporting markdown files...")
    import_files()

    # Step 4: Post the first 'ready' post to Bluesky
    print("\nPosting content to Bluesky...")
    process_ready_post()

if __name__ == "__main__":
    main()

