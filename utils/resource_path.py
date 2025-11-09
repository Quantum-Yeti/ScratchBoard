import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Absolute path for resources (should work for dev & PyInstaller)
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

