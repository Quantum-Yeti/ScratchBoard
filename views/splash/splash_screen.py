from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSpacerItem, QSizePolicy, QApplication
from PySide6.QtGui import QPixmap, QPainterPath, QRegion
from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve

from startup.startup_runner import run_startup
from utils.resource_path import resource_path


def get_current_version() -> str:
    """Read the current version from 'docs/version.txt'."""
    try:
        path = resource_path("docs/version.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        return f"Unknown version ({e})"


class ProgressThread(QThread):
    """Thread to run startup tasks with progress updates."""
    progress = Signal(int, str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func(self.progress.emit)


class SplashScreen(QWidget):
    """Splash screen widget with image, progress bar, messages, and version/copyright info."""

    def __init__(self, image_path: str):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setFixedSize(780, 600)

        # Apply rounded corners and background
        self._apply_rounded_corners(radius=20)
        self._apply_base_style()

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 12, 0, 0)
        self.layout.setSpacing(0)

        # Widgets
        self._setup_image(image_path)
        self.layout.addStretch(1)
        self._add_spacer(height=8)
        self._setup_progress_bar()
        self._setup_message_label()
        self._add_spacer(height=20)
        self._setup_version_label()
        self._setup_copyright_label()

        self.setLayout(self.layout)
        self.show()

        # Animation for smooth progress updates
        self.progress_anim = QPropertyAnimation(self.progress, b"value", self)
        self.progress_anim.setDuration(200)  # Duration per step in ms
        self.progress_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Start the background startup thread
        self.worker = ProgressThread(run_startup)
        self.worker.progress.connect(self.set_progress)
        self.worker.start()

    # Widget Setup Methods
    def _setup_image(self, image_path: str):
        pixmap = QPixmap(image_path)
        self.pixmap = pixmap
        self.label_image = QLabel(self)
        self.label_image.setPixmap(pixmap)
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_image)

    def _setup_progress_bar(self):
        self.progress = QProgressBar(self)
        self.progress.setMaximumWidth(self.pixmap.width())
        self.progress.setMinimumWidth(500)
        self.progress.setFixedHeight(15)  # Thinner modern bar
        self.progress.setValue(0)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #000;
                border-radius: 6px;
                background-color: #505050;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background-color: #00AAE6;
                box-shadow: 0px 0px 6px rgba(0, 191, 255, 0.6);
            }
        """)
        self.layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _setup_message_label(self):
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: white; font-style: italic; margin: 10px;")
        self.layout.addWidget(self.message_label)

    def _setup_version_label(self):
        version = get_current_version()
        self.version_label = QLabel(f"Version: {version}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.version_label)

    def _setup_copyright_label(self):
        current_year = datetime.now().year
        self.copyright_label = QLabel(
            f"\u00A9 {current_year} Quantum Yeti. All rights reserved."
        )
        self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copyright_label.setStyleSheet("padding-bottom: 8px;")
        self.layout.addWidget(self.copyright_label)

    def _add_spacer(self, height: int = 10):
        spacer = QSpacerItem(0, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addItem(spacer)

    # Style Methods
    def _apply_base_style(self):
        """Base widget style including dark background."""
        self.setStyleSheet("""
            QWidget {
                border-radius: 20px;
                background-color: #505050;
            }
        """)
        self._apply_dark_theme()

    def _apply_dark_theme(self):
        """Load custom QSS theme if available."""
        try:
            theme_path = resource_path("ui/themes/main_theme.qss")
            with open(theme_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load {theme_path}: {e}")

    def _apply_rounded_corners(self, radius: int = 20):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # Progress Handling
    def set_progress(self, value: int, message: str = ""):
        """Update progress bar and message."""
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)
        QApplication.processEvents()
        if value >= 100:
            QThread.msleep(300)
            self.finish()

    def finish(self):
        """Close the splash screen."""
        self.close()
