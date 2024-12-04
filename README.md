---

# AutoContentPoster

AutoContentPoster is a Python-based automation tool for managing and posting content to Bluesky. This project simplifies the process of preparing content, importing it into a database, and automatically posting it at scheduled intervals.  

## Features
- **Content Management**: Organize your content in structured folders (`drafts`, `ready`, `processed`).
- **Database Setup**: Automatically creates and maintains a SQLite database to store content and track its status.
- **File Import**: Reads markdown files from the `posts/ready` folder, imports them into the database, and moves them to the `processed` folder.
- **Automated Posting**: Posts the first "ready" entry in the database to Bluesky, updating the status of each post as it is published or if it fails.
- **Folder and File Checks**: Verifies the existence of required folders and lists the markdown files they contain.

## How It Works
1. **Content Preparation**:  
   - Write your content in markdown (`.md`) files and place them in the `posts/ready` folder.

2. **Automated Workflow**:
   - When you run the program, it:
     1. Sets up the database (if not already created).
     2. Verifies folder structure and lists markdown files.
     3. Imports content from `posts/ready` into the database.
     4. Posts the first "ready" item to Bluesky.

3. **Post Status Tracking**:  
   The database tracks the status of each post:
   - `ready`: Imported and waiting to be posted.
   - `posted`: Successfully posted to Bluesky.
   - `failed`: Posting failed, and the post requires attention.

4. **Post Movement**:  
   - After importing, files in `posts/ready` are moved to `posts/processed`.

## Requirements
- Python 3.10 or higher
- Bluesky account credentials
- SQLite (bundled with Python)
- Python packages specified in `requirements.txt`:
  - `python-dotenv`
  - `atproto`

## Setup Instructions
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/AutoContentPoster.git
   cd AutoContentPoster
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Bluesky credentials:
   ```env
   BLUESKY_USERNAME=your_bluesky_username
   BLUESKY_PASSWORD=your_bluesky_password
   ```

5. Ensure the folder structure exists:
   ```bash
   posts/
   ├── drafts/
   ├── ready/
   └── processed/
   ```

6. Run the program:
   ```bash
   python main.py
   ```

## Usage
- Place your `.md` files in the `posts/ready` folder.
- Run `main.py` to process and post content.
- The system will handle importing, posting, and moving files automatically.

## Automating the Workflow
To run the script at scheduled intervals, you can use a task scheduler like `cron` (Linux/macOS) or Task Scheduler (Windows):

### Example `cron` Setup
1. Open the crontab editor:
   ```bash
   crontab -e
   ```

2. Add an entry to run the script every hour:
   ```bash
   0 * * * * /path/to/venv/bin/python /path/to/main.py
   ```

## Known Limitations
- Posts are processed in order of creation.
- Only one post is handled per script run.
- Errors in posting are logged, but retries must be managed manually.

## Future Enhancements (Optional Ideas)
- Implement automated retries for failed posts.
- Add scheduling logic to handle delays between posts.
- Provide a web interface for managing posts.

---
