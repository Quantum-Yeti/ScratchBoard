from PySide6.QtCore import Qt, QUrl, QThread
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

import requests

from helpers.update_helpers.update_checker import UpdateCheckWorker
from utils.resource_path import resource_path



class AboutWidget(QDialog):
    def __init__(self):
        super().__init__()

        # Store the thread
        self.thread = None
        self.worker = None

        # Reserve attribute and store
        self.update_btn = None

        # Window layout setup
        self.setWindowTitle("About Scratch Board")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(400, 420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        layout.addStretch()

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("resources/icons/astronaut.ico")).pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Scratch Board")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Version label
        self.version_label = QLabel("Checking version…")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.version_label)

        # Placeholder for update button
        self.update_btn_layout = QHBoxLayout()
        self.update_btn_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.update_btn_layout)

        # Copyright
        copyright_label = QLabel("© 2025 Quantum Yeti")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(copyright_label)

        # License text
        license_label_txt = QLabel("Use of this software is an agreement to the license below:")
        license_label_txt.setAlignment(Qt.AlignCenter)
        license_label_txt.setWordWrap(True)
        license_label_txt.setStyleSheet("font-size: 12px;")
        layout.addWidget(license_label_txt)

        # License button
        license_btn = QPushButton("View License")
        license_btn.setIcon(QIcon(resource_path("resources/icons/license.png")))
        license_btn.setFixedWidth(120)
        license_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Quantum-Yeti/ScratchBoard/blob/master/LICENSE.md")
        ))

        # Change log button
        change_btn = QPushButton("Change Logs")
        change_btn.setIcon(QIcon(resource_path("resources/icons/changelog.png")))
        change_btn.setFixedWidth(120)
        change_btn.clicked.connect(lambda: QDesktopServices.openUrl("https://github.com/Quantum-Yeti/ScratchBoard/commits/release"))

        # Add buttons to layout
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(license_btn)
        btn_layout.addWidget(change_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # Start threaded update check
        self.start_update_thread()

    # Background Threading Methods for Update Detection
    def start_update_thread(self):
        """Starts GitHub version check in a background thread."""
        self.thread = QThread()
        self.worker = UpdateCheckWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.update_version_label)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def update_version_label(self, current_version, latest_version):
        """Called when the background thread returns update info."""

        if latest_version is None:
            self.version_label.setText(f"Version {current_version} (Check failed)")
            return

        cur = current_version.lstrip("vV")
        latest = latest_version.lstrip("vV")

        if cur == latest:
            self.version_label.setText(f"Version {current_version} (Up-to-date)")

            # Remove update button if it exists
            if self.update_btn:
                self.update_btn.setParent(None)
                self.update_btn = None

        else:
            self.version_label.setText(
                f"Version {current_version} (Update available: {latest_version})"
            )

            # Create update button only once
            if not self.update_btn:
                self.update_btn = QPushButton("Get Update")
                self.update_btn.setIcon(QIcon(resource_path("resources/icons/update.png")))
                self.update_btn.setFixedWidth(130)

                # Open GitHub release asset
                self.update_btn.clicked.connect(
                    lambda: QDesktopServices.openUrl(
                        QUrl(
                            f"https://github.com/Quantum-Yeti/ScratchBoard/releases/download/{latest_version}/ScratchBoard.exe"
                        )
                    )
                )

                self.update_btn_layout.addWidget(self.update_btn)
