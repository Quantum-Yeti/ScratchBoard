import time
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSpacerItem, QSizePolicy, QApplication
from PySide6.QtGui import QPixmap, QCloseEvent
from PySide6.QtCore import Qt, QTimer, QThread, Signal

from helpers.startup.run_startup import run_startup
from utils.resource_path import resource_path
from views.dashboard_view import DashboardView


class ProgressThread(QThread):
    progress = Signal(int, str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        # Call the function and pass a callback to emit progress
        self.func(self.progress.emit)

class SplashScreen(QWidget):
    def __init__(self, image_path: str):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        self.setFixedSize(780, 600)

        # Apply dark theme
        self.apply_dark_theme()

        # Layout
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)

        # Image Label
        self.pixmap = QPixmap(image_path)
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.label_image)

        self.vbox.addStretch(1)

        # Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setMaximumWidth(self.pixmap.width())
        self.progress.setMinimumWidth(500)
        self.progress.setFixedHeight(30)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.vbox.addWidget(self.progress, alignment=Qt.AlignHCenter)

        # Message Label
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: white;")
        self.vbox.addWidget(self.message_label)

        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)  # 10px vertical space
        self.vbox.addItem(spacer)

        # Copyright label
        current_year = datetime.now().year
        self.copyright_label = QLabel(self)
        self.copyright_label.setText(f"\u00A9 {current_year} Quantum Yeti. All rights reserved.")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.copyright_label)

        self.setLayout(self.vbox)
        self.show()

        self.worker = ProgressThread(run_startup)
        self.worker.progress.connect(self.set_progress)
        self.worker.start()

    # Helper Methods
    def apply_dark_theme(self):
        try:
            with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f" Failed to load {resource_path('ui/themes/main_theme.qss')}: {e}")

    def set_progress(self, value: int, message: str = ""):
        """Update progress bar and optional message"""
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)

        if value >= 100:
            self.finish()

        # Force UI to update immediately
        self.repaint()

    def finish(self):
        self.close()