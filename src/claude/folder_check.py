from pathlib import Path

def check_folders():
    project_root = Path(__file__).parent.parent
    folders = [
        project_root / "posts" / "drafts",
        project_root / "posts" / "ready",
        project_root / "posts" / "processed"
    ]
    
    for folder in folders:
        status = "✓" if folder.exists() else "✗"
        md_files = list(folder.glob("*.md")) if folder.exists() else []
        print(f"{status} {folder.name}")
        print(f"Contains {len(md_files)} markdown files")

if __name__ == "__main__":
    check_folders()

