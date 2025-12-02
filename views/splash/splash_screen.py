import time
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSpacerItem, QSizePolicy, QApplication
from PySide6.QtGui import QPixmap, QPainterPath, QRegion
from PySide6.QtCore import Qt, QThread, Signal, QRectF

from helpers.startup.run_startup import run_startup
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

class ProgressThread(QThread):
    """
    QThread subclass that runs a function in a separate thread and emit the progress bar updates.
    """
    progress = Signal(int, str)

    def __init__(self, func):
        """
        Initialize the thread with the progress function.
        """
        super().__init__()
        self.func = func

    def run(self):
        """
        Execute the thread function, passing the progress bar signal's emit method as a callback.
        """
        self.func(self.progress.emit)

class SplashScreen(QWidget):
    """
    Splash screen widget class that includes an image, progress bar, message label, and copyright notice.

    Attributes:
        vbox (QVBoxLayout): Main layout container.
        label_image (QLabel): Displays the splash image.
        progress (QProgressBar): Shows progress of startup tasks.
        message_label (QLabel): Displays optional progress messages.
        copyright_label (QLabel): Displays copyright information.
        worker (ProgressThread): Thread running startup tasks.
    """
    def __init__(self, image_path: str):
        """
        Initialize the splash screen widget.
        """
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(780, 600)
        self.round_corner_window(radius=20)
        self.setStyleSheet("""
        QWidget {
            border-radius: 20px;
            background-color: #505050;
        }    
        """)

        # Apply dark theme
        self.apply_dark_theme()

        # Main vertical layout
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 12, 0, 0)
        self.vbox.setSpacing(0)

        # Load and display splash screen background image
        self.pixmap = QPixmap(image_path)
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.label_image)

        # Stretchable space pushes progress bar and copyright to bottom
        self.vbox.addStretch(1)

        # Initialize Progress Bar
        self.progress = QProgressBar(self)
        self.progress.setMaximumWidth(self.pixmap.width())
        self.progress.setMinimumWidth(500)
        self.progress.setFixedHeight(30)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                font-size: 12px;
                font-weight: bold;
            }
            
        """)

        self.vbox.addWidget(self.progress, alignment=Qt.AlignHCenter)

        # Initialize message label reserved for progress bar text
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: white; font-style: italic;")
        self.vbox.addWidget(self.message_label)

        # Spacer to add a vertical gap
        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)  # 10px vertical space
        self.vbox.addItem(spacer)

        # Initialize Version label
        current_version = get_current_version()
        self.version_label = QLabel(f"Version: {current_version}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.vbox.addWidget(self.version_label)

        # Initialize copyright label with the current year
        current_year = datetime.now().year
        self.copyright_label = QLabel(self)
        self.copyright_label.setText(f"\u00A9 {current_year} Quantum Yeti. All rights reserved.")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setStyleSheet("padding-bottom: 8px;")
        self.vbox.addWidget(self.copyright_label)

        self.setLayout(self.vbox)
        self.show()

        # Start the asynchronous worker thread to run startup tasks
        self.worker = ProgressThread(run_startup)
        self.worker.progress.connect(self.set_progress)
        self.worker.start()

    # Helper Methods
    def apply_dark_theme(self):
        """
        Method to load the main_theme style from the resource path.
        Throws an exception if the theme cannot be loaded.
        """
        try:
            with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f" Failed to load {resource_path('ui/themes/main_theme.qss')}: {e}")

    def round_corner_window(self, radius=20):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def set_progress(self, value: int, message: str = ""):
        """
        Update the progress bar value and display the step message.
        """
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)

        QApplication.processEvents()

        if value >= 100:
            QThread.msleep(300)
            self.finish()

        # Force UI to update immediately
        self.repaint()

    def finish(self):
        """
        Finish and close the splash screen.
        """
        self.close()