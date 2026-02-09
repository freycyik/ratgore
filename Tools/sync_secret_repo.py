#!/usr/bin/env python3
"""
Script for synchronizing files from a secret repository.
Clones the secret repository and copies its files to the current project,
overwriting existing files with the latest versions.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ========== CONFIGURATION ==========
# Directory for cloning the secret repository
SECRET_REPO_DIR = "./secret-repo-temp"
# Current project directory
CURRENT_REPO_DIR = "."

# Files and directories to ignore during copy
IGNORE_PATTERNS = {
    ".git",
    ".github",
    "README.md",
    ".gitignore",
    ".gitattributes"
}

def log(message: str):
    """
    Logs a message with a prefix.

    Args:
        message: The message to log
    """
    print(f"[SYNC] {message}", flush=True)

def clone_secret_repo(token: str, url: str):
    """
    Clones the secret repository into a temporary directory.

    Args:
        token: GitHub token with read access to the repository
        url: URL of the secret repository
    """
    log(f"Cloning secret repository: {url}")

    # Remove old directory if it exists
    if os.path.exists(SECRET_REPO_DIR):
        log(f"Removing old directory: {SECRET_REPO_DIR}")
        shutil.rmtree(SECRET_REPO_DIR)

    # Format URL with token for HTTPS
    if url.startswith("https://"):
        # Extract the part after https://
        repo_path = url.replace("https://", "")
        auth_url = f"https://{token}@{repo_path}"
    elif url.startswith("git@"):
        # For SSH, use the URL as is (requires SSH_PRIVATE_KEY)
        auth_url = url
    else:
        raise ValueError(f"Unsupported URL format: {url}")

    try:
        subprocess.run(
            ["git", "clone", "--depth=1", auth_url, SECRET_REPO_DIR],
            check=True,
            capture_output=True,
            text=True
        )
        log("Repository cloned successfully")
    except subprocess.CalledProcessError as e:
        log(f"ERROR during cloning: {e.stderr}")
        sys.exit(1)

def should_ignore(file_path: Path) -> bool:
    """
    Checks if a file or directory should be ignored.

    Args:
        file_path: Path to the file relative to the root of the secret repository

    Returns:
        True if the file should be ignored
    """
    parts = file_path.parts

    # Check each part of the path
    for part in parts:
        if part in IGNORE_PATTERNS:
            return True

    # Check the full file name
    if file_path.name in IGNORE_PATTERNS:
        return True

    return False

def sync_files():
    """
    Copies files from the secret repository to the current project.
    Overwrites existing files and creates new ones.
    """
    log("Starting file synchronization...")

    secret_repo_path = Path(SECRET_REPO_DIR)
    current_repo_path = Path(CURRENT_REPO_DIR)

    if not secret_repo_path.exists():
        log("ERROR: Secret repository directory not found")
        sys.exit(1)

    copied_count = 0
    overwritten_count = 0
    skipped_count = 0

    # Recursively iterate through all files in the secret repository
    for file_path in secret_repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Get the relative path
        relative_path = file_path.relative_to(secret_repo_path)

        # Check if the file should be ignored
        if should_ignore(relative_path):
            log(f"Skipping (ignored): {relative_path}")
            skipped_count += 1
            continue

        # Determine the destination path
        dest_path = current_repo_path / relative_path

        # Create directories if they don't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        file_existed = dest_path.exists()
        shutil.copy2(file_path, dest_path)

        if file_existed:
            log(f"Overwritten: {relative_path}")
            overwritten_count += 1
        else:
            log(f"Copied: {relative_path}")
            copied_count += 1

    log(f"\n=== Synchronization Summary ===")
    log(f"New files copied: {copied_count}")
    log(f"Existing files overwritten: {overwritten_count}")
    log(f"Files skipped: {skipped_count}")
    log(f"Total files processed: {copied_count + overwritten_count + skipped_count}")

def cleanup():
    """Removes the temporary directory with the secret repository."""
    if os.path.exists(SECRET_REPO_DIR):
        log(f"Removing temporary directory: {SECRET_REPO_DIR}")
        shutil.rmtree(SECRET_REPO_DIR)

def main():
    """Main function of the script."""
    log("=== Starting synchronization with the secret repository ===")

    # Get environment variables
    token = os.getenv("SECRET_REPO_TOKEN")
    url = os.getenv("SECRET_REPO_URL")

    if not token:
        log("ERROR: SECRET_REPO_TOKEN environment variable not set")
        sys.exit(1)

    if not url:
        log("ERROR: SECRET_REPO_URL environment variable not set")
        sys.exit(1)

    try:
        # Clone the secret repository
        clone_secret_repo(token, url)

        # Synchronize files
        sync_files()

        log("=== Synchronization completed successfully ===")

    except Exception as e:
        log(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Clean up temporary files
        cleanup()

if __name__ == "__main__":
    main()
