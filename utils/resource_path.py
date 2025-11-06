import sys
import os
import matplotlib

def resource_path(relative_path: str) -> str:
    """
    Absolute path for resources (should work for dev & PyInstaller)
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def configure_matplotlib():
    """
    Ensure matplotlib can find its data (fonts, styles) when frozen by PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # For PyInstaller
        try:
            base_path = sys._MEIPASS
            mpl_data_path = os.path.join(base_path, "mpl-data")
            matplotlib.rcParams['datapath'] = mpl_data_path
            print(f"Matplotlib datapath set to: {mpl_data_path}")
        except Exception as e:
            print(f"Failed to configure matplotlib datapath: {e}")
    else:
        # Running normally (dev)
        print(f"Matplotlib datapath (dev) = {matplotlib.get_data_path()}")
