from pathlib import Path
import os
import sys

def resource_path(relative_path: str, data=False):
    """
    Returns absolute path to resources.

    Args:
        relative_path (str): path relative to project root (dev) or PyInstaller bundle.
        data (bool): if True, path is for user data → go to LOCALAPPDATA
    """
    if data:
        # User data path
        base_data_dir = Path(os.getenv("LOCALAPPDATA")) / "ScratchBoardData"
        base_data_dir.mkdir(parents=True, exist_ok=True)
        return str(base_data_dir / relative_path)

    # App resource path
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)

    # Development path: relative to project root
    base_dir = Path(__file__).parent.parent  # adjust as needed
    return str(base_dir / relative_path)