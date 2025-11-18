from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from utils.resource_path import resource_path

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
        layout.setAlignment(Qt.AlignCenter)

        # App Icon
        icon_label = QLabel()
        icon = QIcon(resource_path("resources/icons/astronaut.ico"))
        icon_label.setPixmap(icon.pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # App Name
        title_label = QLabel("Scratch Board")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(version_label)

        # Copyright
        copyright_label = QLabel("\u00A9 2025 Quantum Yeti")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(copyright_label)

        # License text
        license_label_txt = QLabel("Use of this software is an agreement to the license below:")
        license_label_txt.setAlignment(Qt.AlignCenter)
        license_label_txt.setStyleSheet("font-size: 12px;")
        layout.addWidget(license_label_txt)

        # License button
        license_btn_icon = QIcon(resource_path("resources/icons/license.png"))
        license_btn = QPushButton("View License")
        license_btn.setIcon(license_btn_icon)
        license_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Quantum-Yeti/ScratchBoard/blob/master/LICENSE.md")
        ))

        # Close button
        btn_icon = QIcon(resource_path("resources/icons/cancel.png"))
        close_btn = QPushButton("Close")
        close_btn.setIcon(btn_icon)
        close_btn.setFixedWidth(70)
        close_btn.clicked.connect(self.close)

        # Combined button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(license_btn)
        btn_layout.addSpacing(20)  # Space between buttons
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
