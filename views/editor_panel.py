from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QHBoxLayout, QMessageBox
)
from utils.resource_path import resource_path


class EditorPanel(QDialog):
    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")

        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        # Window size
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setObjectName("EditorPanel")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title editor
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Enter title here...")
        self.title_edit.setObjectName("TitleEdit")

        # Content editor
        self.content_edit = QTextEdit(content)
        self.content_edit.setPlaceholderText("Write your note here...")
        self.content_edit.setObjectName("ContentEdit")

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_note)
        btn_layout.addWidget(save_btn)

        # Delete button (only if editing)
        if self.delete_callback:
            delete_btn = QPushButton("Delete")
            delete_btn.setIcon(QIcon(resource_path("resources/icons/delete.png")))
            delete_btn.setObjectName("DeleteButton")
            delete_btn.clicked.connect(self.delete_note)
            btn_layout.addWidget(delete_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(QIcon(resource_path("resources/icons/cancel.png")))
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        # Final assembly
        layout.addWidget(self.title_edit)
        layout.addWidget(self.content_edit)
        layout.addLayout(btn_layout)

        # Stylesheet
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

    def delete_note(self):
        if not self.delete_callback:
            return

        reply = QMessageBox.question(
            self,
            "Delete Note?",
            "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.delete_callback(self.note_id)
            self.accept()
