from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from utils.resource_path import resource_path


def create_section_title(text, icon_name, icon_size=32):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignHCenter)

    icon_label = QLabel()
    pixmap = QPixmap(resource_path(f"resources/icons/{icon_name}.png"))
    pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    icon_label.setPixmap(pixmap)
    icon_label.setContentsMargins(0, 12, 0, 0)

    text_label = QLabel(text)
    text_label.setFixedHeight(icon_size)
    text_label.setStyleSheet(
        "font-weight: bold; font-size: 16px; color: white; margin-top: 10px; font-family: Segoe UI;")

    layout.addWidget(icon_label)
    layout.addWidget(text_label)

    return container
