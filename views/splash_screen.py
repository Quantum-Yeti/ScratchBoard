# views/splash_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtCore import Qt

class SplashScreen(QWidget):
    def __init__(self, image_path: str):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 300)  # Adjust to your image size

        # Set background pixmap
        self.pixmap = QPixmap(image_path)
        self.label_image = QLabel(self)
        self.label_image.setPixmap(self.pixmap)
        self.label_image.setAlignment(Qt.AlignCenter)

        # Overlay layout
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.label_image)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setFixedHeight(20)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.vbox.addWidget(self.progress)

        # Message label
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: white;")
        self.vbox.addWidget(self.message_label)

        self.setLayout(self.vbox)
        self.show()

    def set_progress(self, value: int, message: str = ""):
        """Update progress bar and optional message"""
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)
        # Process events so UI updates
        self.repaint()
