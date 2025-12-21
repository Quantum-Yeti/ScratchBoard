import datetime
import os
import shutil
from pathlib import Path


def sync_db(db_path, onedrive_folder=None):
    if not os.path.exists(db_path):
        print("The database path doesn't exist")
        return

    if onedrive_folder is None:
        onedrive_folder = os.path.join(os.path.expanduser("~"), "OneDrive", "ScratchBoard")

    Path(onedrive_folder).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(db_path)
    dest_path = os.path.join(onedrive_folder, f"{timestamp}_{filename}")

    try:
        shutil.copy(db_path, dest_path)
        print("The database has been synced to OneDrive: {dest_path}.")
    except Exception as e:
        print(f"Failed to sync {db_path}: {e}")
