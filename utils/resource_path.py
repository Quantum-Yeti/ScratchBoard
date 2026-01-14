import sys
import os

def resource_path(relative_path):
    """Return absolute path to resources in dev and PyInstaller."""
    # Note to self - When running inside PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # Note to self - When running in development:
    # Use the project root (one level above utils/)
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)



