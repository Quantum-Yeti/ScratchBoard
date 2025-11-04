from PySide6.QtGui import QIcon, QTextCursor, QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel,
    QSplitter, QWidget, QTextBrowser, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QUrl

from helpers.render_markdown_to_html import render_markdown_to_html
from utils.resource_path import resource_path

class EditorPanel(QDialog):
    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        self.resize(1000, 600)
        self.setMinimumSize(800, 400)

        # --- Main layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # --- Title editor ---
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Enter title here...")
        main_layout.addWidget(self.title_edit)

        # --- Splitter for editor and preview ---
        splitter = QSplitter(Qt.Horizontal)

        # --- Left: Markdown Editor ---
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        editor_label = QLabel("Markdown Editor")
        editor_label.setAlignment(Qt.AlignCenter)
        editor_layout.addWidget(editor_label)

        # Toolbar buttons
        toolbar_layout = QHBoxLayout()
        buttons = [
            ("Bold", "**", "**"),
            ("Italic", "_", "_"),
            ("Header", "# ", ""),
            ("Link", "[", "](https://)"),
            ("Code", "`", "`"),
            ("Quote", "> ", ""),
            ("UL", "- ", ""),
            ("OL", "1. ", "")
        ]
        for text, start, end in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, s=start, e=end: self.insert_md(s, e))
            toolbar_layout.addWidget(btn)
        toolbar_layout.addStretch()
        editor_layout.addLayout(toolbar_layout)

        # Markdown editor QTextEdit
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(content)
        self.content_edit.textChanged.connect(self.update_preview_debounce)
        editor_layout.addWidget(self.content_edit, stretch=1)
        splitter.addWidget(editor_widget)

        # --- Right: Preview ---
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Preview")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_label)

        self.preview = QTextBrowser()
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(False)
        self.preview.anchorClicked.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview, stretch=1)
        splitter.addWidget(preview_widget)

        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)

        # --- Bottom buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.clicked.connect(self.save_note)
        btn_layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setIcon(QIcon(resource_path("resources/icons/delete.png")))
        if self.delete_callback:
            delete_btn.clicked.connect(self.delete_note)
        else:
            delete_btn.setEnabled(False)
        btn_layout.addWidget(delete_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(QIcon(resource_path("resources/icons/cancel.png")))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # --- Initial rendering ---
        self.update_preview()
        self.load_stylesheet()

    def showEvent(self, event):
        """Render preview after showing the dialog to ensure QTextBrowser updates."""
        super().showEvent(event)
        self.update_preview()

    # --- Markdown helpers ---
    def insert_md(self, start, end):
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
        """Render Markdown using the helper function"""
        raw_text = self.content_edit.toPlainText()
        self.preview.setHtml(render_markdown_to_html(raw_text))

    def update_preview_debounce(self):
        if hasattr(self, "update_timer") and self.update_timer.isActive():
            self.update_timer.stop()
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(200)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start()

    # --- Save/Delete ---
    def save_note(self):
        """Save note with Markdown intact (formatting preserved)."""
        self.save_callback(self.title_edit.text(), self.content_edit.toPlainText())
        self.accept()

    def delete_note(self):
        if not self.delete_callback:
            return
        reply = QMessageBox.question(
            self, "Delete Note?", "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_callback(self.note_id)
            self.accept()

    # --- Load QSS stylesheet ---
    def load_stylesheet(self):
        try:
            qss_path = resource_path("ui/themes/editor.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor.qss:", e)
