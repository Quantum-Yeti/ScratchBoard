# views/editor_panel.py
import os
import re
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QSize, QPropertyAnimation
from PySide6.QtGui import QIcon, QTextCursor, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel,
    QSplitter, QTextBrowser, QSizePolicy, QMessageBox, QWidget, QToolBar, QGraphicsOpacityEffect
)
from PySide6.QtGui import QAction

from helpers.count_words import count_words
from helpers.drag_drop_image import save_qimage, save_file_drop
from helpers.markdown_to_html import render_markdown_to_html
from utils.resource_path import resource_path


class EditorPanel(QDialog):

    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None):
        super().__init__(parent)

        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self._is_fullscreen = False

        self.setWindowTitle("Edit Note")
        self.resize(1100, 700)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ---------------- Title
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Title...")
        layout.addWidget(self.title_edit)

        # ---------------- Splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # ---------------- Left (Editor)
        left = QWidget()
        left_l = QVBoxLayout(left)
        self.toolbar = QToolBar()
        self._add_toolbar_actions()
        left_l.addWidget(self.toolbar)

        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(content or "")
        self.content_edit.textChanged.connect(self._schedule_preview)
        self.content_edit.textChanged.connect(self._update_word_stats)
        left_l.addWidget(self.content_edit, stretch=1)
        splitter.addWidget(left)

        # ---------------- Right (Preview)
        self.preview = QTextBrowser()
        self.preview.setObjectName("PreviewPanel")
        self.preview.setAutoFillBackground(True)


        left_l.addWidget(self.preview, stretch=1)
        self.preview.setOpenExternalLinks(True)
        self._opacity = QGraphicsOpacityEffect(self.preview)
        self.preview.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1)
        splitter.addWidget(self.preview)

        splitter.setSizes([620, 480])

        # ---------------- Bottom Row
        bottom = QHBoxLayout()
        self.word_label = QLabel("Words: 0 — Chars: 0")
        bottom.addWidget(self.word_label)
        bottom.addStretch()

        btn_save = QPushButton(QIcon(resource_path("resources/icons/save.png")), "Save")
        btn_save.clicked.connect(self.save_note)
        bottom.addWidget(btn_save)

        btn_delete = QPushButton(QIcon(resource_path("resources/icons/delete.png")), "Delete")
        if delete_callback:
            btn_delete.clicked.connect(self.delete_note)
        else:
            btn_delete.setEnabled(False)
        bottom.addWidget(btn_delete)

        btn_cancel = QPushButton(QIcon(resource_path("resources/icons/cancel.png")), "Cancel")
        btn_cancel.clicked.connect(self.reject)
        bottom.addWidget(btn_cancel)

        layout.addLayout(bottom)

        # ---------------- Keyboard Shortcuts
        self._bind_shortcuts()

        # ---------------- Debounce timer for preview
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
        self._preview_timer.timeout.connect(self._update_preview_no_animation)

        # Initial load
        self._update_word_stats()
        self._update_preview_no_animation()
        self.load_stylesheet()

    # Toolbar Helpers
    def _add_toolbar_actions(self):
        def add(icon, start, end, tip):
            act = self.toolbar.addAction(QIcon(resource_path(f"resources/icons/{icon}")), "")
            act.setToolTip(tip)
            act.triggered.connect(lambda: self.insert_md(start, end))

        add("bold.png", "**", "**", "Bold")
        add("italic.png", "_", "_", "Italic")
        add("header.png", "# ", "", "Header")
        add("link.png", "[", "](https://)", "Link")
        add("code_block.png", "```\n", "\n```", "Code Block")
        add("quote.png", "> ", "", "Quote")
        add("bullet.png", "- ", "", "Bullet List")

        img = self.toolbar.addAction(QIcon(resource_path("resources/icons/insert_image.png")), "")
        img.setToolTip("Insert image")
        img.triggered.connect(self._insert_image_dialog)

        fs = self.toolbar.addAction(QIcon(resource_path("resources/icons/full_screen.png")), "")
        fs.setToolTip("Fullscreen (F11)")
        fs.triggered.connect(self.toggle_fullscreen)

    def insert_md(self, start, end):
        cur = self.content_edit.textCursor()
        if cur.hasSelection():
            txt = cur.selectedText()
            cur.insertText(f"{start}{txt}{end}")
        else:
            cur.insertText(f"{start}{end}")
            cur.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end))
        self._schedule_preview()

    # Preview Rendering
    def _schedule_preview(self):
        self._preview_timer.start()

    def _update_preview_no_animation(self):
        md = self.content_edit.toPlainText()
        html = render_markdown_to_html(md)
        html = self._convert_image_paths(html)
        self.preview.setHtml(html)

    # Word Count
    def _update_word_stats(self):
        text = self.content_edit.toPlainText()
        words, chars = count_words(text)
        self.word_label.setText(f"Words: {words} — Chars: {chars}")

    # Drag & Drop Image
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        md_img = None
        if event.mimeData().hasImage():
            md_img = save_qimage(event.mimeData().imageData())
        else:
            for url in event.mimeData().urls():
                md_img = save_file_drop(url.toLocalFile())
                if md_img:
                    break

        if md_img:
            self.content_edit.insertPlainText("\n" + md_img + "\n")
            self._schedule_preview()
            event.acceptProposedAction()

    def _convert_image_paths(self, html):
        def replace(match):
            path = match.group(1)
            abs_path = os.path.abspath(path).replace("\\", "/")
            return f'src="file:///{abs_path}"'

        return re.sub(r'src="([^"]+)"', replace, html)

    def _insert_image_dialog(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if path:
            dst_dir = Path("data/images")
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / Path(path).name
            import shutil
            shutil.copy(path, dst)

            md = f"\n![image]({dst.as_posix()})\n"
            self.content_edit.insertPlainText(md)
            self._schedule_preview()

    # Save/Delete
    def save_note(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title before saving.")
            return
        self.save_callback(title, self.content_edit.toPlainText())
        self.accept()

    def delete_note(self):
        if self.delete_callback and QMessageBox.question(self, "Delete?",
                "Delete this note?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.delete_callback(self.note_id)
            self.accept()


    # Shortcuts / Fullscreen
    def _bind_shortcuts(self):
        def ks(key, handler):
            act = QAction(self)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(handler)
            self.addAction(act)

        ks("Ctrl+s", self.save_note)
        ks("Ctrl+b", lambda: self.insert_md("**", "**"))
        ks("Ctrl+i", lambda: self.insert_md("_", "_"))
        ks("Ctrl+k", lambda: self.insert_md("[", "](https://)"))
        ks("F11", self.toggle_fullscreen)

    def toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self._is_fullscreen = not self._is_fullscreen

    # Style
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/editor.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor.qss:", e)
