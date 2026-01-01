
import os
import re
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QEvent, QUrl
from PySide6.QtGui import QIcon, QTextCursor, QKeySequence, QAction, QPixmap
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextBrowser, QLabel, QPushButton, QToolBar, QStackedWidget,
    QMessageBox, QGraphicsOpacityEffect, QComboBox, QSizePolicy
)

from helpers.ui_helpers.image_pop import ImagePopup
from models.note_model import NoteModel
from ui.fonts.font_list import main_font_list
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.custom_q_edit import CustomQEdit
from utils.resource_path import resource_path
from managers.editor_manager import EditorManager

class EditorPanel(QDialog):
    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None, tags=None):
        super().__init__(parent)
        self.note_model = NoteModel()
        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self._is_fullscreen = False

        self.setWindowTitle("Scratch Board: Edit Note")
        self.resize(1100, 700)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setAcceptDrops(True)

        # Layouts
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 12)
        layout.setSpacing(10)

        # Top Row: Title + Tags
        top_row = QHBoxLayout()
        self.title_edit = QLineEdit(title)
        self.title_edit.setPlaceholderText("Title...")
        top_row.addWidget(self.title_edit, stretch=2)

        self.add_tag = QLineEdit()
        self.add_tag.setPlaceholderText("Tags: (e.g., tag1, tag2)")
        if tags:
            self.add_tag.setText(", ".join(tags))
        top_row.addWidget(self.add_tag, stretch=1)
        layout.addLayout(top_row)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("EditorToolbar")
        self._add_toolbar_actions()

        # Stacked widget: editor + preview
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        # Editor page
        editor_page = QWidget()
        editor_layout = QVBoxLayout(editor_page)
        editor_layout.setContentsMargins(0,0,0,0)
        editor_layout.addWidget(self.toolbar)

        # Content in the edit screen
        self.content_edit = CustomQEdit()
        self.content_edit.setAcceptRichText(True)
        self.content_edit.setStyleSheet("background-color: #333; color: #fff;")
        self.content_edit.setStyleSheet(vertical_scrollbar_style)
        self.content_edit.setHtml(EditorManager.load_initial_content(content))
        self.content_edit.setPlaceholderText("Use Plaintext, Markdown syntax, or the buttons to write and format.")
        self.content_edit.textChanged.connect(self._schedule_preview)
        self.content_edit.textChanged.connect(self._update_word_stats)
        editor_layout.addWidget(self.content_edit, stretch=1)
        self.stack.addWidget(editor_page)

        # Preview screen
        preview_page = QWidget()
        preview_layout = QVBoxLayout(preview_page)
        preview_layout.setContentsMargins(0,0,0,0)
        self.preview = QTextBrowser()
        self.preview.setObjectName("PreviewPanel")
        self.preview.setPlaceholderText("This preview panel renders your Markdown/PlainText as Html.")
        self.preview.setOpenLinks(False)
        self.preview.installEventFilter(self)
        self.preview.setOpenExternalLinks(True)
        self.preview.setStyleSheet("background-color: #333; color: #fff;")
        self.preview.setStyleSheet(vertical_scrollbar_style)
        self.preview.anchorClicked.connect(self._on_preview_link_clicked)
        self._opacity = QGraphicsOpacityEffect(self.preview)
        self.preview.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1)
        preview_layout.addWidget(self.preview)
        self.stack.addWidget(preview_page)

        # Bottom row
        bottom = QHBoxLayout()

        # Word count section
        self.word_label = QLabel("Words: 0 — Chars: 0")
        self.word_label.setContentsMargins(10,0,0,0)
        bottom.addWidget(self.word_label)

        # Creation date
        self.update_label = QLabel()
        bottom.addWidget(self.update_label)

        bottom.addStretch()

        # Toggle editor/preview
        self.toggle_button = QPushButton("Preview")
        self.toggle_button.setIcon(QIcon(resource_path("resources/icons/toggle.png")))
        self.toggle_button.clicked.connect(self.toggle_preview)
        bottom.addWidget(self.toggle_button)

        # Save note button
        btn_save = QPushButton("Save")
        btn_save.setIcon(QIcon(resource_path("resources/icons/save.png")))
        btn_save.clicked.connect(self.save_note)
        bottom.addWidget(btn_save)

        # Delete note button
        btn_delete = QPushButton("Delete")
        btn_delete.setIcon(QIcon(resource_path("resources/icons/delete.png")))
        if delete_callback:
            btn_delete.clicked.connect(self.delete_note)
        else:
            btn_delete.setEnabled(False)
        bottom.addWidget(btn_delete)

        # Cancel button
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setIcon(QIcon(resource_path("resources/icons/cancel.png")))
        btn_cancel.clicked.connect(self.reject)
        bottom.addWidget(btn_cancel)
        layout.addLayout(bottom)

        # Shortcuts
        self._bind_shortcuts()

        # Preview timer
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
        self._preview_timer.timeout.connect(self._update_preview_no_animation)

        # Initial update
        self._update_word_stats()
        self._update_timestamps()
        self._update_preview_no_animation()
        self.load_stylesheet()

    ### --- Editor/Preview Toggle --- ###
    def toggle_preview(self):
        if self.stack.currentIndex() == 0:
            self._update_preview_no_animation()
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("Edit")
        else:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("Preview")

    ### --- Word count --- ###
    def _update_word_stats(self):
        words, chars = EditorManager.count_words_and_chars(self.content_edit.toPlainText())
        self.word_label.setText(f"Words: {words} — Chars: {chars}")

    ### --- Timestamps --- ###
    def _update_timestamps(self):
        """Update the creation and modification timestamps for the note file."""
        note = self.note_model.get_note_by_id(self.note_id) # fetch from DB
        if note:
            #created = note["created"]  # ISO string from SQLite
            updated = note["updated"]
            #created_dt = datetime.fromisoformat(created)
            updated_dt = datetime.fromisoformat(updated)
            #self.created_label.setText(f"Created: {created_dt.strftime('%Y-%m-%d %H:%M')}")
            self.update_label.setText(f"Updated: {updated_dt.strftime('%Y-%m-%d')}")
        else:
            #self.created_label.setText("Created: N/A")
            self.update_label.setText("Updated: N/A")

    ### --- Preview update --- ###
    def _schedule_preview(self):
        self._preview_timer.start()

    def _update_preview_no_animation(self):
        html = self.content_edit.toHtml()
        self.preview.setHtml(EditorManager.prepare_preview(html))

    ### --- Toolbar actions --- ###
    def _add_toolbar_actions(self):
        def action(icon, handler, tip):
            act = self.toolbar.addAction(QIcon(resource_path(f"resources/icons/{icon}")), "")
            act.setToolTip(tip)
            act.triggered.connect(handler)

        # Text styles
        action("bold.png", lambda: EditorManager.bold(self.content_edit.textCursor()), "Bold")
        action("italic.png", lambda: EditorManager.italic(self.content_edit.textCursor()), "Italic")

        # Headers
        action("header1.png", lambda: EditorManager.header(self.content_edit.textCursor(), 18), "Header 1")
        action("header2.png", lambda: EditorManager.header(self.content_edit.textCursor(), 15), "Header 2")
        action("header3.png", lambda: EditorManager.header(self.content_edit.textCursor(), 13), "Header 3")

        # Alignment
        action("align_left.png", lambda: EditorManager.align_left(self.content_edit.textCursor()), "Align left")
        action("align_center.png", lambda: EditorManager.align_center(self.content_edit.textCursor()), "Align center")
        action("align_right.png", lambda: EditorManager.align_right(self.content_edit.textCursor()), "Align right")

        # Lists
        action("bullet.png", lambda: EditorManager.bullet_list(self.content_edit.textCursor()), "Bullet List")
        action("numbered.png", lambda: EditorManager.numbered_list(self.content_edit.textCursor()), "Numbered List")

        # Insert horizontal line
        action("hr.png", lambda: EditorManager.insert_hr(self.content_edit.textCursor()), "Horizontal Line")

        # Highlight / Text color
        # --- Highlight / Text color ---
        action("highlight.png", lambda: EditorManager.highlight(self.content_edit.textCursor(), parent=self),"Highlight")
        action("text_color.png", lambda: EditorManager.text_color(self.content_edit.textCursor(), parent=self), "Text Color")

        # Insert images
        img = self.toolbar.addAction(QIcon(resource_path("resources/icons/insert_image.png")), "")
        img.setToolTip("Insert Image")
        img.triggered.connect(lambda: EditorManager.insert_image_via_dialog(self, self.content_edit.textCursor()))

        # Insert links
        action("link.png", lambda: EditorManager.insert_link(self, self.content_edit.textCursor()), "Insert Link")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        # Font family combo box selector (controlled list)
        self.font_combo = QComboBox()
        self.font_combo.setFixedWidth(150)

        for font_name in main_font_list:
            self.font_combo.addItem(font_name)

        font_name_label = QLabel("Font: ")
        self.font_combo.setCurrentText("Segoe UI")
        self.font_combo.currentTextChanged.connect(self._set_font_family_from_name)
        self.toolbar.addWidget(font_name_label)
        self.toolbar.addWidget(self.font_combo)

        # Spacing between font and size
        self.toolbar.addWidget(self._toolbar_spacer(12))

        # Font size combo box
        font_size_label = QLabel("Size: ")
        self.font_size_combo = QComboBox()
        self.font_size_combo.setEditable(True)
        self.font_size_combo.setFixedWidth(80)

        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32]:
            self.font_size_combo.addItem(str(size))

        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self._set_font_size)
        self.toolbar.addWidget(font_size_label)
        self.toolbar.addWidget(self.font_size_combo)

    ### --- Font Combo Helpers --- ###
    def _set_font_size(self, size_str: str):
        try:
            size = float(size_str)
        except ValueError:
            return

        cursor = self.content_edit.textCursor()
        if not cursor:
            return

        fmt = cursor.charFormat()
        fmt.setFontPointSize(size)
        cursor.mergeCharFormat(fmt)

    def _set_font_family_from_name(self, font_name: str):
        cursor = self.content_edit.textCursor()
        if not cursor:
            return

        fmt = cursor.charFormat()
        fmt.setFontFamily(font_name)
        cursor.mergeCharFormat(fmt)

    def _toolbar_spacer(self, width=4):
        spacer = QWidget()
        spacer.setFixedWidth(width)
        return spacer

    ### --- Shortcuts --- ###
    def _bind_shortcuts(self):
        def ks(key, handler):
            act = QAction(self)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(handler)
            self.addAction(act)

        ks("F11", self._toggle_fullscreen)

    ### --- Markdown insertion --- ###
    def insert_md(self, start, end):
        cur = self.content_edit.textCursor()
        if cur.hasSelection():
            txt = cur.selectedText()
            cur.insertText(f"{start}{txt}{end}")
        else:
            cur.insertText(f"{start}{end}")
            cur.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(end))
        self._schedule_preview()

    ### --- Fullscreen --- ###
    def _toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self._is_fullscreen = not self._is_fullscreen

    ### --- Save/Delete --- ###
    def save_note(self):
        title = self.title_edit.text().strip()
        tags = [t.strip() if t.startswith("#") else "#" + t.strip() for t in re.split(r"[,\s]+", self.add_tag.text().strip()) if t.strip()]
        tags = list(dict.fromkeys(tags))
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title before saving.")
            return
        self.save_callback(title, self.content_edit.toHtml(), tags)
        self.accept()

    def delete_note(self):
        if self.delete_callback and QMessageBox.question(self, "Delete?", "Delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.delete_callback(self.note_id)
            self.accept()

    ### --- Drag & Drop --- ###
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        md_img = None
        if event.mimeData().hasImage():
            from utils.image_io import save_qimage
            md_img = save_qimage(event.mimeData().imageData())
        else:
            from utils.image_io import save_file_drop
            for url in event.mimeData().urls():
                md_img = save_file_drop(url.toLocalFile())
                if md_img: break

        if md_img:
            self.content_edit.insertPlainText("\n" + md_img + "\n")
            self._schedule_preview()
            event.acceptProposedAction()

    ### --- Preview link/image clicks --- ###
    def eventFilter(self, obj, event):
        if obj is self.preview and event.type() == QEvent.Type.MouseButtonRelease:
            cursor = self.preview.cursorForPosition(event.position().toPoint())
            anchor = cursor.charFormat().anchorHref()
            kind, path = EditorManager.handle_preview_link(anchor)
            if kind == "image":
                self._show_image(path)
                return True
        return super().eventFilter(obj, event)

    def _on_preview_link_clicked(self, url: QUrl):
        kind, path = EditorManager.handle_preview_link(url.toString())
        if kind == "image":
            self._show_image(path)

    def open_existing_in_preview(self):
        """Open the note directly in preview mode."""
        self._update_preview_no_animation()  # ensure preview is up to date
        self.stack.setCurrentIndex(1)        # switch to preview page
        self.toggle_button.setText("Edit")   # update button text/icon


    def _show_image(self, path):
        """Open an image using the ImagePopup helper."""
        if not os.path.exists(path):
            return
        ImagePopup.show(self, path)

    ### --- Load stylesheet --- ###
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/editor_view_theme.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor_view_theme.qss:", e)
