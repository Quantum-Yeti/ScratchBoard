import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and PyInstaller.

    Usage:
        icon_path = resource_path("icons/add.png")
        qss_path = resource_path("ui/themes/dark.qss")
    """

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

