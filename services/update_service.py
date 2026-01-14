from PySide6.QtCore import QObject, Signal
import requests
from utils.resource_path import resource_path

def get_current_version():
    """Reads current version from version.txt."""
    try:
        with open(resource_path("docs/version.txt"), "r") as f:
            return f.read().strip()
    except Exception:
        return "v0.0"


def get_latest_release():
    """Deprecated: Fetch the latest GitHub release tag."""
    url = "https://api.github.com/repos/Quantum-Yeti/ScratchBoard/releases/latest"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.json().get("tag_name")
    except requests.RequestException:
        return None


class UpdateCheckWorker(QObject):
    finished = Signal(str, str)  # current_version, latest_version
    def run(self):
        current = get_current_version()
        latest = get_latest_release()
        self.finished.emit(current, latest)
