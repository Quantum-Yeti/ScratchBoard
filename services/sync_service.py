import datetime
import os
import shutil
from pathlib import Path


def sync_db(db_path, onedrive_folder=None):
    """
    Sync the local sb_data folder to the OneDrive folder with a timestamped filename.

    This function copies the database file at db_path to the OneDrive folder on Windows. If
    no OneDrive folder is specified, it defaults to '~/OneDrive/ScratchBoard'. The destination file is prefixed
    with the current date and time to avoid overwriting previous backups.
    """

    # Checks if the source database file exists
    if not os.path.exists(db_path):
        print("The database path doesn't exist")
        return

    # If OneDrive folder is not provided, set a default  path
    if onedrive_folder is None:
        onedrive_folder = os.path.join(os.path.expanduser("~"), "OneDrive", "ScratchBoard")

    # Create a OneDrive folder if it doesn't exist
    Path(onedrive_folder).mkdir(parents=True, exist_ok=True)

    # Generate a timestamp for the backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract the original filename from the database  path
    filename = os.path.basename(db_path)

    # Build the full destination path
    dest_path = os.path.join(onedrive_folder, f"{timestamp}_{filename}")

    # Try copying the database to the OneDrive folder
    try:
        shutil.copy(db_path, dest_path)
        print("The database has been synced to OneDrive: {dest_path}.")
    except Exception as e:
        # Catch any errors and display the stacktrace
        print(f"Failed to sync {db_path}: {e}")
