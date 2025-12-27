from PySide6.QtWidgets import QTextEdit
from pygments.lexers import q


class CustomQEdit(QTextEdit):
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        s