import os
import sqlite3
from dotenv import load_dotenv
from atproto import Client
from datetime import datetime

# Load environment variables
load_dotenv()

# Define database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'content.db')
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')

if not BLUESKY_USERNAME or not BLUESKY_PASSWORD:
   raise ValueError("Bluesky credentials not found in .env file")

def post_to_bluesky(content):
   try:
       client = Client()
       client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
       response = client.post(text=content)
       return True, response
   except Exception as e:
       return False, str(e)

def process_ready_post():
   conn = sqlite3.connect(DB_PATH)
   cursor = conn.cursor()

   cursor.execute('SELECT id, content FROM posts WHERE status = "ready" ORDER BY created_at LIMIT 1')
   row = cursor.fetchone()

   if row:
       post_id, content = row
       success, result = post_to_bluesky(content)

       if success:
           cursor.execute('''
               UPDATE posts
               SET status = "posted",
                   posted_at = datetime('now')
               WHERE id = ?
           ''', (post_id,))
           print(f"Successfully posted content ID: {post_id}")
       else:
           cursor.execute('''
               UPDATE posts
               SET status = "failed"
               WHERE id = ?
           ''', (post_id,))
           print(f"Failed to post content ID: {post_id}")
           print(f"Error: {result}")
   else:
       print("No ready posts found")

   conn.commit()
   conn.close()

if __name__ == "__main__":
   process_ready_post()

