from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTextEdit, QLineEdit
from pygments.lexers import q


class CustomQEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Force white text
        self.setTextColor(QColor.fromRgb(255, 255, 255))

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())

