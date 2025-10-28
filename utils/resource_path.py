import sys
import os
import matplotlib

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

# --- Matplotlib fix for PyInstaller ---
def configure_matplotlib():
    try:
        # Get PyInstaller's temp folder
        base_path = os.path.dirname(os.path.abspath(__file__))
        mpl_data_path = os.path.join(base_path, 'mpl-data')

        # Only set datapath if the rcParam still exists
        if 'datapath' in matplotlib.rcParams:
            matplotlib.rcParams['datapath'] = mpl_data_path
    except Exception as e:
        print(f"Matplotlib configuration skipped: {e}")

