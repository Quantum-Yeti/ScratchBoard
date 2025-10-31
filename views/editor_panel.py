from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QSplitter, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from utils.resource_path import resource_path
import markdown2


class EditorPanel(QDialog):
    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        self.resize(1000, 600)
        self.setMinimumSize(800, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # --- Title editor ---
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Enter title here...")
        self.title_edit.setObjectName("TitleEdit")
        main_layout.addWidget(self.title_edit)

        # --- Editor / Preview splitter ---
        splitter = QSplitter(Qt.Horizontal)

        # Left side (Editor)
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        editor_label = QLabel("Markdown Editor")
        editor_label.setAlignment(Qt.AlignCenter)
        editor_layout.addWidget(editor_label)

        # Markdown toolbar
        toolbar_layout = QHBoxLayout()
        bold_btn = QPushButton("Bold")
        bold_btn.clicked.connect(lambda: self.insert_md("**", "**"))
        italic_btn = QPushButton("Italic")
        italic_btn.clicked.connect(lambda: self.insert_md("_", "_"))
        heading_btn = QPushButton("Header")
        heading_btn.clicked.connect(lambda: self.insert_md("# ", ""))
        link_btn = QPushButton("Link")
        link_btn.clicked.connect(lambda: self.insert_md("[", "](url)"))
        code_btn = QPushButton("Code")
        code_btn.clicked.connect(lambda: self.insert_md("`", "`"))

        for btn in [bold_btn, italic_btn, heading_btn, link_btn, code_btn]:
            btn.setFixedWidth(60)
            toolbar_layout.addWidget(btn)
        toolbar_layout.addStretch()
        editor_layout.addLayout(toolbar_layout)

        self.content_edit = QTextEdit(content)
        self.content_edit.textChanged.connect(self.update_preview)
        editor_layout.addWidget(self.content_edit)
        splitter.addWidget(editor_widget)

        # Right side (Preview)
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Preview")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_label)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        preview_layout.addWidget(self.preview)
        splitter.addWidget(preview_widget)

        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.clicked.connect(self.save_note)
        btn_layout.addWidget(save_btn)

        if self.delete_callback:
            delete_btn = QPushButton("Delete")
            delete_btn.setIcon(QIcon(resource_path("resources/icons/delete.png")))
            delete_btn.clicked.connect(self.delete_note)
            btn_layout.addWidget(delete_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(QIcon(resource_path("resources/icons/cancel.png")))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Initial preview
        self.update_preview()
        self.load_stylesheet()

    # --- Markdown helpers ---
    def insert_md(self, start, end):
        """Insert Markdown syntax at cursor."""
        cursor = self.content_edit.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{start}{selected}{end}")
        else:
            cursor.insertText(f"{start}{end}")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end))
            self.content_edit.setTextCursor(cursor)
        self.content_edit.setFocus()

    def update_preview(self):
        """Render Markdown live in the preview."""
        raw_text = self.content_edit.toPlainText()
        html = markdown2.markdown(raw_text)
        self.preview.setHtml(html)

    def save_note(self):
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()
        self.save_callback(title, content)
        self.accept()

    def delete_note(self):
        if not self.delete_callback:
            return
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Delete Note?", "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_callback(self.note_id)
            self.accept()

    def load_stylesheet(self):
        try:
            qss_path = resource_path("ui/themes/editor.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor.qss:", e)
