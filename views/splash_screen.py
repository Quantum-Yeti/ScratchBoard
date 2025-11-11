# views/splash_screen.py
from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTextBrowser
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from utils.resource_path import resource_path

class SplashScreen(QWidget):
    def __init__(self, image_path: str):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 300)  # Adjust to your image size

        # Apply dark theme
        self.apply_dark_theme()

        # Title Label
        self.title_label = QLabel("Scratch Board", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            "QLabel { font-size: 20pt; font-weight: bold; color: white; }"
        )

        # Image Label
        self.pixmap = QPixmap(image_path)
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignCenter)

        # Layout
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.title_label)
        self.vbox.addWidget(self.label_image)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setFixedHeight(20)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.vbox.addWidget(self.progress)

        # Message Label
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: white;")
        self.vbox.addWidget(self.message_label)

        # Developer Label (Clickable Link)
        self.dev_label = QLabel(self)
        self.dev_label.setText(
            '<a href="https://github.com/Quantum-Yeti/ScratchBoard"'
            'style="text-decoration: none; color: cyan;">'
            'Developed by Quantum-Yeti</a>'
        )
        self.dev_label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # allow clicking
        self.dev_label.setOpenExternalLinks(True)  # opens in default browser
        self.dev_label.setAlignment(Qt.AlignCenter)
        self.dev_label.setStyleSheet("""
            QLabel {
                color: red;
                font-style: italic;
                font-weight: bold;
                background: transparent;
                text-decoration: none;
            }
            QLabel:hover {
                color: cyan;
            }
        """)
        self.dev_label.setOpenExternalLinks(True)
        self.vbox.addWidget(self.dev_label)

        self.setLayout(self.vbox)
        self.show()

    # Helper Methods
    def apply_dark_theme(self):
        try:
            with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f" Failed to load {resource_path('ui/themes/dark_theme.qss')}: {e}")

    def set_progress(self, value: int, message: str = ""):
        """Update progress bar and optional message"""
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)

        # Force UI to update immediately
        self.repaint()
