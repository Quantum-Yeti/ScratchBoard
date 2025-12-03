import os
import re
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QIcon, QTextCursor, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel,
    QSplitter, QTextBrowser, QMessageBox, QWidget, QToolBar, QGraphicsOpacityEffect
)
from PySide6.QtGui import QAction

from helpers.calc_helpers.count_words import count_words
from helpers.image_helpers.drag_drop_image import save_qimage, save_file_drop
from helpers.markdown_helpers.md_preview import get_markdown_guide
from helpers.markdown_helpers.md_to_html import render_markdown_to_html
from ui.menus.context_menu import ModifyContextMenu
from utils.resource_path import resource_path


class EditorPanel(QDialog):

    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None, tags=None):
        super().__init__(parent)

        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self._is_fullscreen = False

        self.setWindowTitle("Scratch Board: Edit Note")
        self.resize(1100, 700)
        #self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlags (Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 12)
        layout.setSpacing(10)

        # Horizontal layout for Title + Tags
        top_row = QHBoxLayout()

        # Title
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Title...")
        top_row.addWidget(self.title_edit, stretch=2)

        # Tags
        self.add_tag = QLineEdit()
        self.add_tag.setPlaceholderText("Add Tags: #tag1, #tag2...")
        if tags:
            self.add_tag.setText(", ".join(tags))
        top_row.addWidget(self.add_tag, stretch=1)

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(top_row)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        layout.addWidget(splitter, stretch=1)

        # Left side (Editor)
        left = QWidget()
        left_l = QVBoxLayout(left)

        self.toolbar = QToolBar()
        self._add_toolbar_actions()
        left_l.addWidget(self.toolbar)

        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(content or "")
        self.content_edit.setPlaceholderText(get_markdown_guide())
        self.content_edit.textChanged.connect(self._schedule_preview)
        self.content_edit.textChanged.connect(self._update_word_stats)
        left_l.addWidget(self.content_edit, stretch=1)

        splitter.addWidget(left)

        # Right side (Preview)
        self.preview = QTextBrowser()
        self.preview.setObjectName("PreviewPanel")
        self.preview.setPlaceholderText("Markdown -> Html Preview")
        self.preview.setAutoFillBackground(True)
        self.preview.setContentsMargins(0,0,6,0)
        self.preview.setOpenLinks(False)
        self.preview.installEventFilter(self)
        self.preview.setOpenExternalLinks(True)

        self._opacity = QGraphicsOpacityEffect(self.preview)
        self.preview.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1)

        splitter.addWidget(self.preview)


        # initial sizes for left and right panels
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # Bottom Row
        bottom = QHBoxLayout()
        self.word_label = QLabel("Words: 0 — Chars: 0")
        self.word_label.setContentsMargins(10, 0, 0, 0)
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

        # Keyboard Shortcuts
        self._bind_shortcuts()

        # Debounce timer for preview
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
        add("header1.png", "# ", "", "Header")
        add("header2.png", "## ", "", "Header 2")
        add("header3.png", "### ", "", "Header 3")
        add("link.png", "[Website title...", "](https://...)", "Link")
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

    def eventFilter(self, obj, event):
        if obj is self.preview and event.type() == QEvent.MouseButtonDblClick:
            cursor = self.preview.cursorForPosition(event.pos())
            anchor = cursor.charFormat().anchorHref()

            if anchor:
                # Trigger the full-view popup
                from PySide6.QtCore import QUrl
                self._on_preview_link_clicked(QUrl(anchor))
                return True

        return super().eventFilter(obj, event)

    # Preview Rendering
    def _schedule_preview(self):
        self._preview_timer.start()

    def _update_preview_no_animation(self):
        md = self.content_edit.toPlainText()
        html = render_markdown_to_html(md)
        html = self._convert_image_paths(html)

        # Force background from HTML so QTextBrowser obeys it
        style = """
            <style>
            body {
                background-color: #333;
            }
            </style>
            """

        self.preview.setHtml(style + html)

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

        html = re.sub(r'src="([^"]+)"', replace, html)

        # Wrap IMG in clickable <a>
        html = re.sub(
            r'<img([^>]+)src="([^"]+)"([^>]*)>',
            r'<a href="\2"><img\1src="\2"\3></a>',
            html
        )

        return html

    def _insert_image_dialog(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if path:
            dst_dir = Path("sb_data/images")
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
        tag_text = self.add_tag.text().strip()

        multi_tags = re.split(r"[,\s]+", tag_text)

        tags = []
        for t in multi_tags:
            t = t.strip()
            if not t:
                continue
            if not t.startswith("#"):
                t = "#" + t
            tags.append(t)

        tags = list(dict.fromkeys(tags))

        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title before saving.")
            return
        self.save_callback(title, self.content_edit.toPlainText(), tags)
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

    def _on_preview_link_clicked(self, url):
        """Opens image_helpers in a full-window dialog."""
        path = url.toLocalFile()

        if not os.path.exists(path):
            return

        from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QScrollArea
        from PySide6.QtGui import QPixmap

        dlg = QDialog(self)
        dlg.setWindowTitle("Image Viewer")
        dlg.resize(900, 700)

        layout = QVBoxLayout(dlg)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)

        pix = QPixmap(path)
        lbl.setPixmap(pix)
        scroll.setWidget(lbl)

        dlg.exec()

    # Style
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/editor_view_theme.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor_view_theme.qss:", e)
