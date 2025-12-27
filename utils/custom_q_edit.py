from PySide6.QtWidgets import QTextEdit, QLineEdit
from pygments.lexers import q


class CustomQEdit(QTextEdit):
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())

