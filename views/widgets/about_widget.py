from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

import requests

from utils.resource_path import resource_path

def get_latest_release(repo_owner="Quantum-Yeti", repo_name="ScratchBoard"):
    """Fetches the latest release tag from GitHub."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("tag_name")  # e.g., "v1.0.1"
    except Exception as e:
        print("Failed to fetch latest release:", e)
        return None

class AboutWidget(QDialog):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("About Scratch Board")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(400, 400)
        self.setModal(True)

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter | Qt.AlignVCenter)  # Top and center horizontally

        # App Icon
        icon_label = QLabel()
        icon = QIcon(resource_path("resources/icons/astronaut.ico"))
        icon_label.setPixmap(icon.pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # App Name
        title_label = QLabel("Scratch Board")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Version label
        current_version = "v1.1"
        latest_version = get_latest_release()
        if latest_version and latest_version != current_version:
            version_text = f"Version {current_version} (Update available: {latest_version})"
        else:
            version_text = f"Version {current_version} (Up-to-date)"

        version_label = QLabel(version_text)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(version_label)

        # Copyright
        copyright_label = QLabel("\u00A9 2025 Quantum Yeti")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(copyright_label)

        # License text
        license_label_txt = QLabel(
            "Use of this software is an agreement to the license below:"
        )
        license_label_txt.setAlignment(Qt.AlignCenter)
        license_label_txt.setWordWrap(True)  # wrap long text
        license_label_txt.setStyleSheet("font-size: 12px;")
        layout.addWidget(license_label_txt)

        # License button
        license_btn_icon = QIcon(resource_path("resources/icons/license.png"))
        license_btn = QPushButton("View License")
        license_btn.setIcon(license_btn_icon)
        license_btn.setFixedWidth(120)
        license_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Quantum-Yeti/ScratchBoard/blob/master/LICENSE.md")
        ))

        # Close button
        #close_btn_icon = QIcon(resource_path("resources/icons/cancel.png"))
        #close_btn = QPushButton("Close")
        #close_btn.setIcon(close_btn_icon)
        #close_btn.setFixedWidth(80)
        #close_btn.clicked.connect(self.close)

        # Buttons layout (centered)
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)  # center horizontally
        btn_layout.setSpacing(20)  # space between buttons
        btn_layout.addWidget(license_btn)
        #btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def update_version_label(self):
        latest_version = get_latest_release()
        if latest_version:
            # Remove leading 'v' if present
            latest_version_clean = latest_version.lstrip("vV")
            current_version_clean = self.current_version.lstrip("vV")

            if latest_version_clean != current_version_clean:
                self.version_label.setText(
                    f"Version {self.current_version} (Update available: {latest_version_clean})"
                )
            else:
                self.version_label.setText(f"Version {self.current_version} (Up-to-date)")
        else:
            self.version_label.setText(f"Version {self.current_version} (Check failed)")

