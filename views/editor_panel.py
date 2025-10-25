from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QHBoxLayout
)
from utils.resource_path import resource_path

class EditorPanel(QDialog):
    def __init__(self, parent, title, content, save_callback):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.save_callback = save_callback

        # Window sizing
        self.resize(800, 600)
        self.setMinimumSize(600, 400)

        # Object name for styling
        self.setObjectName("EditorPanel")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title input
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Enter title here...")
        self.title_edit.setObjectName("TitleEdit")

        # Content input
        self.content_edit = QTextEdit(content)
        self.content_edit.setPlaceholderText("Write your note here...")
        self.content_edit.setObjectName("ContentEdit")

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_note)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        # Assemble
        layout.addWidget(self.title_edit)
        layout.addWidget(self.content_edit)
        layout.addLayout(btn_layout)

        # Apply stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        try:
            qss_path = resource_path("ui/themes/editor.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor.qss:", e)

    def save_note(self):
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        self.save_callback(title, content)
        self.accept()
