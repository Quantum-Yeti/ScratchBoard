from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import requests
import os
import sys
import tempfile
import subprocess
from utils.resource_path import resource_path  # your resource helper

GITHUB_REPO = "Quantum-Yeti/ScratchBoard"
CURRENT_VERSION = "1.0"

class UpdateDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Update Available")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setModal(True)
        self.setFixedSize(350, 150)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel("Checking for updates...")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.update_btn = QPushButton("Update Now")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self.download_and_update)
        layout.addWidget(self.update_btn)

        self.check_latest_release()

    def check_latest_release(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.latest_version = data["tag_name"]
            self.download_url = None

            # Look for Windows exe in assets
            for asset in data["assets"]:
                if asset["name"].endswith(".exe"):
                    self.download_url = asset["browser_download_url"]
                    break

            if not self.download_url:
                self.info_label.setText("No Windows release found.")
                return

            if self.latest_version > CURRENT_VERSION:
                self.info_label.setText(f"Version {self.latest_version} is available!")
                self.update_btn.setEnabled(True)
            else:
                self.info_label.setText("You are using the latest version.")
        except Exception as e:
            self.info_label.setText(f"Update check failed: {e}")

    def download_and_update(self):
        if not self.download_url:
            return

        try:
            tmp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(tmp_dir, f"ScratchBoard_update.exe")
            self.info_label.setText("Downloading update...")

            # Download the new exe
            with requests.get(self.download_url, stream=True) as r:
                r.raise_for_status()
                with open(new_exe_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Launch updater script
            current_exe = sys.executable
            updater_script = os.path.join(os.path.dirname(current_exe), "updater.py")
            subprocess.Popen([sys.executable, updater_script, new_exe_path, current_exe])

            # Close main app
            QMessageBox.information(self, "Updating", "App will restart to apply update.")
            sys.exit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download update: {e}")
