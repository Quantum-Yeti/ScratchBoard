from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from datetime import datetime

from utils.resource_path import resource_path

def get_current_version():
    """
    Reads the current version from of the program from 'docs/version.txt'.

    Returns:
        str: The current version of the program or 'Unknown version' if it fails.
    """
    try:
        path = resource_path("docs/version.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"Unknown version ({e})"


def style_centered_button(btn):
    """
    Applies style to icon and text for QPushbutton within the AboutWidget class.
    """
    # Apply padding and icon size styling
    btn.setStyleSheet("""
        QPushButton {
            padding: 6px;
            qproperty-iconSize: 18px;
        }
    """)

    # Sets icon size explicitly
    btn.setIconSize(QSize(18, 18))

    # Ensure icon is on the left, text to the right
    btn.setLayoutDirection(Qt.LeftToRight)

    # Center text inside the button
    btn.setStyleSheet("text-align: center;")

class AboutWidget(QDialog):
    """
    A QDialog widget class that displays information about the Scratch Board program such as
    version, license, commits, and links to potential updates.
    """
    def __init__(self):
        super().__init__()

        # Window layout setup
        self.setWindowTitle("Scratch Board: About Scratch Board")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(400, 420)
        self.setModal(True)

        # Main vertical layout for window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Add a stretch to the top for spacing
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
        current_version = get_current_version()
        self.version_label = QLabel(f"Version: {current_version}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.version_label)

        # Check for update button
        self.update_btn = QPushButton("Check Updates")
        self.update_btn.setToolTip("Check for Updates")
        self.update_btn.setIcon(QIcon(resource_path("resources/icons/update.png")))

        # Connect button to Github releases
        self.update_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(f"https://github.com/Quantum-Yeti/ScratchBoard/releases/")
        ))
        layout.addWidget(self.update_btn, alignment=Qt.AlignHCenter)

        # Copyright
        year = datetime.now().year
        copyright_label = QLabel(f"© {year} Quantum Yeti")
        copyright_label.setToolTip(f"© {year} Quantum Yeti")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: #5F8A8B;")
        layout.addWidget(copyright_label)

        # License text
        license_label_txt = QLabel("Use of this software is an agreement to the license below:")
        license_label_txt.setAlignment(Qt.AlignCenter)
        license_label_txt.setWordWrap(True)
        license_label_txt.setStyleSheet("font-size: 12px;")
        layout.addWidget(license_label_txt)

        # License button
        license_btn = QPushButton("View License")
        license_btn.setToolTip("View License")
        license_btn.setIcon(QIcon(resource_path("resources/icons/license.png")))
        license_btn.setFixedWidth(120)
        style_centered_button(license_btn)
        license_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Quantum-Yeti/ScratchBoard/blob/master/LICENSE.md")
        ))

        # Commit log button
        commits_btn = QPushButton("Commits")
        commits_btn.setToolTip("Commits")
        commits_btn.setIcon(QIcon(resource_path("resources/icons/changelog.png")))
        commits_btn.setFixedWidth(120)
        style_centered_button(commits_btn)
        commits_btn.clicked.connect(lambda: QDesktopServices.openUrl("https://github.com/Quantum-Yeti/ScratchBoard/commits/master/"))

        # Add buttons to layout
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(license_btn)
        btn_layout.addWidget(commits_btn)
        layout.addLayout(btn_layout)

        # Bottom stretch for spacing
        layout.addStretch()

