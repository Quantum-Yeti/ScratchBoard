from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QHBoxLayout
from utils.resource_path import resource_path

class EditorPanel(QDialog):
    def __init__(self, parent, title, content, save_callback):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.save_callback = save_callback

        # Set initial size
        self.resize(800, 600)  # width x height
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        self.title_edit = QLineEdit(title)
        self.content_edit = QTextEdit(content)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_note)
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))

        layout.addWidget(self.title_edit)
        layout.addWidget(self.content_edit)
        layout.addWidget(save_btn)

    def save_note(self):
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        self.save_callback(title, content)
        self.accept()
