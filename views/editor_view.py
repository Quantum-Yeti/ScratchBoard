import os
import re
import shutil
import webbrowser
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QUrl
from PySide6.QtGui import QIcon, QTextCursor, QKeySequence, QAction, QPixmap
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextBrowser, QLabel, QPushButton, QToolBar, QStackedWidget,
    QScrollArea, QFileDialog, QMessageBox, QGraphicsOpacityEffect
)

from helpers.calc_helpers.count_words import count_words
from helpers.image_helpers.drop_img import save_qimage, save_file_drop
from helpers.md_helpers.md_to_html import render_markdown_to_html
from ui.menus.context_menu import ModifyContextMenu
from utils.resource_path import resource_path


def _convert_image_paths(html):
    """
    Convert all <img> tags in the provided HTML to use absolute file URLs
    and wrap them in clickable links.

    This function searches for all <img> tags in the HTML, converts their
    `src` attribute to an absolute path with the `file:///` scheme, and
    wraps the image in an <a> tag so that it can be clicked (e.g., to open
    in a popup).

    Args:
        html (str): The input HTML containing <img> tags with relative paths.

    Returns:
        str: The modified HTML with <img> tags converted to absolute file URLs
             and wrapped in clickable <a> tags.
    """
    def repl(m):
        src = m.group(1)
        abs_path = os.path.abspath(src).replace("\\", "/")
        # Wrap image in <a> with clickable link
        return f'<a href="file:///{abs_path}"><img src="file:///{abs_path}"></a>'

    # Match all <img src="...">
    html = re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', repl, html)
    return html


class EditorPanel(QDialog):
    """
    A rich text editor dialog for creating and editing notes with Markdown support,
    live HTML preview, image insertion, and tagging.

    Features:
        - Title and tag input fields.
        - Markdown editor with toolbar for formatting (bold, italic, headers, links, code blocks, lists).
        - Drag-and-drop image support and image insertion dialog.
        - Live HTML preview with clickable images.
        - Word and character count display.
        - Keyboard shortcuts for common actions (save, bold, italic, link insertion, fullscreen toggle).
        - Fullscreen toggle with F11.
        - Save and optional delete functionality via callbacks.

    Args:
        parent (QWidget): The parent widget for this dialog.
        note_id (Any): Unique identifier for the note being edited.
        title (str): Initial title of the note.
        content (str): Initial content of the note (plain text or Markdown).
        save_callback (Callable): Function to call when the note is saved.
            Should accept parameters: title, content, tags.
        delete_callback (Optional[Callable]): Function to call when the note is deleted.
            Should accept the note_id as a parameter. Defaults to None.
        tags (Optional[List[str]]): Initial tags for the note. Defaults to None.
    """
    def __init__(self, parent, note_id, title, content, save_callback, delete_callback=None, tags=None):
        super().__init__(parent)

        self.note_id = note_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback
        self._is_fullscreen = False

        self.setWindowTitle("Scratch Board: Edit Note")
        self.resize(1100, 700)
        #self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
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

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("EditorToolbar")
        self._add_toolbar_actions()

        # Stacked Widget (Editor / Preview)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        # Editor Toggle
        editor_page = QWidget()
        editor_layout = QVBoxLayout(editor_page)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.addWidget(self.toolbar)

        self.content_edit = ModifyContextMenu()
        self.content_edit.setPlainText(content or "")
        self.content_edit.setPlaceholderText("Use Plaintext, Markdown syntax, or the buttons to write and format.")
        self.content_edit.textChanged.connect(self._schedule_preview)
        self.content_edit.textChanged.connect(self._update_word_stats)
        editor_layout.addWidget(self.content_edit, stretch=1)

        self.stack.addWidget(editor_page)  # index 0

        # Preview Toggle
        preview_page = QWidget()
        preview_layout = QVBoxLayout(preview_page)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        self.preview = QTextBrowser()
        self.preview.setObjectName("PreviewPanel")
        self.preview.setPlaceholderText("This preview panel renders your Markdown/PlainText as Html.")
        self.preview.setAutoFillBackground(True)
        self.preview.setContentsMargins(0,0,6,0)
        self.preview.setOpenLinks(False)
        self.preview.installEventFilter(self)
        self.preview.setOpenExternalLinks(True)
        self.preview.anchorClicked.connect(self._on_preview_link_clicked)

        self._opacity = QGraphicsOpacityEffect(self.preview)
        self.preview.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1)

        preview_layout.addWidget(self.preview)
        self.stack.addWidget(preview_page)  # index 1

        # Bottom Row
        bottom = QHBoxLayout()
        self.word_label = QLabel("Words: 0 — Chars: 0")
        self.word_label.setContentsMargins(10, 0, 0, 0)
        bottom.addWidget(self.word_label)
        bottom.addStretch()

        # Toggle Preview Button
        self.toggle_button = QPushButton(QIcon(resource_path("resources/icons/preview.png")), "Preview")
        self.toggle_button.setStyleSheet("""
            QPushButton:hover {
                background-color: rgb(70, 130, 180);
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_preview)
        bottom.addWidget(self.toggle_button)

        # Save button
        btn_save = QPushButton(QIcon(resource_path("resources/icons/save.png")), "Save")
        btn_save.clicked.connect(self.save_note)
        bottom.addWidget(btn_save)

        # Delete button
        btn_delete = QPushButton(QIcon(resource_path("resources/icons/delete.png")), "Delete")
        if delete_callback:
            btn_delete.clicked.connect(self.delete_note)
        else:
            btn_delete.setEnabled(False)
        bottom.addWidget(btn_delete)

        # Cancel button
        btn_cancel = QPushButton(QIcon(resource_path("resources/icons/cancel.png")), "Cancel")
        btn_cancel.clicked.connect(self.reject)
        bottom.addWidget(btn_cancel)

        # Add the bottom layout
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

    #### --- Toggle Editor/Preview --- ####
    def toggle_preview(self):
        """
        Toggle between the editor view and the preview view.

        Updates the stacked widget to show either the editor or the preview.
        Also updates the toggle button text accordingly.
        """
        if self.stack.currentIndex() == 0:
            self._update_preview_no_animation()
            self.stack.setCurrentIndex(1)
            self.toggle_button.setText("Edit")
            self.toggle_button.setIcon(QIcon(resource_path("resources/icons/edit_btn.png")))
        else:
            self.stack.setCurrentIndex(0)
            self.toggle_button.setText("Preview")
            self.toggle_button.setIcon(QIcon(resource_path("resources/icons/preview.png")))

    #### --- Markdown Insertion --- ####
    def insert_md(self, start, end):
        """
        Insert Markdown formatting around the current text selection or at the cursor.

        If the user has selected text, this method wraps the selection with the
        provided `start` and `end` strings (e.g., "**" for bold). If no text is
        selected, it inserts `start` and `end` at the cursor and positions the
        cursor between them for immediate typing.

        Args:
            start (str): The Markdown prefix to insert before the selection or cursor.
            end (str): The Markdown suffix to insert after the selection or cursor.
        """
        cur = self.content_edit.textCursor()
        if cur.hasSelection():
            txt = cur.selectedText()
            cur.insertText(f"{start}{txt}{end}")
        else:
            cur.insertText(f"{start}{end}")
            cur.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(end))
        self._schedule_preview()

    #### --- Event Filter for Preview Links --- ####
    def eventFilter(self, obj, event):
        """
        Intercept and handle events for child widgets, specifically detecting
        clicks on image links in the preview panel.

        When the event originates from the preview QTextBrowser and is a
        mouse button release, this method checks if the clicked position corresponds
        to an <a> tag linking to a local file (file:///). If the file exists, it
        opens the image in a full-window viewer.

        Args:
            obj (QObject): The object where the event occurred.
            event (QEvent): The event to filter.

        Returns:
            bool: True if the event was handled (image link clicked), otherwise
            delegates to the default event filter.
        """
        if obj is self.preview and event.type() == QEvent.Type.MouseButtonRelease:
            cursor = self.preview.cursorForPosition(event.position().toPoint())
            anchor = cursor.charFormat().anchorHref()

            if anchor.startswith("file:///"):
                path = anchor[8:] if anchor.startswith("file:///") else anchor
                if os.path.exists(path):
                    self._on_preview_img_clicked(path)
                    return True

        return super().eventFilter(obj, event)

    #### --- Drag & Drop --- ####
    def dragEnterEvent(self, event):
        """
        Handle drag enter events for the editor panel.

        Accepts the drag if it contains an image or file URLs, allowing
        the user to drop images or files onto the editor.

        Args:
            event (QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """
        Handle drop events on the editor panel.

        Processes dropped images or files:
        - If an image is dropped, saves it and inserts a Markdown image tag.
        - If file URLs are dropped, saves the first valid file and inserts a Markdown image tag.

        After insertion, schedules a preview update and accepts the drop.

        Args:
            event (QDropEvent): The drop event containing images or file URLs.
        """
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

    #### --- Save/Delete --- ####
    def save_note(self):
        """
        Save the current note with its title, content, and tags.

        - Retrieves the title from the title input field.
        - Parses and normalizes tags from the tag input field (adds '#' if missing and removes duplicates).
        - Warns the user if the title is empty and cancels saving.
        - Calls the save callback with the title, content, and processed tags.
        - Closes the editor dialog upon successful save.
        """
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
        """
        Delete the current note after user confirmation.

        - Prompts the user with a Yes/No dialog to confirm deletion.
        - If confirmed and a delete callback is provided, calls the callback with the note ID.
        - Closes the editor dialog after deletion.
        """
        if self.delete_callback and QMessageBox.question(
            self,
            "Delete?",
            "Delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.delete_callback(self.note_id)
                self.accept()

    #### --- INTERNAL HELPERS --- ####
    def _schedule_preview(self):
        """
        Start or restart the preview update timer.

        This method triggers a short-delay timer that will eventually
        call the preview update function. It is used to debounce
        rapid text changes for efficient Markdown rendering.
        """
        self._preview_timer.start()

    def _update_preview_no_animation(self):
        """
        Render the current Markdown content to HTML and update the preview panel.

        This method converts the editor's Markdown text into HTML, processes
        image paths to be absolute and clickable, and injects inline CSS for
        consistent styling. Images are constrained to a max width of 250px,
        maintain aspect ratio, and are centered with a pointer cursor.
        """
        md = self.content_edit.toPlainText()
        html = render_markdown_to_html(md)
        html = _convert_image_paths(html)

        # Force background from HTML so QTextBrowser obeys it
        style = """
            <style>
                body {
                    background-color: #333;
                    color: #fff;
                    font-family: sans-serif;
                }
                img { 
                    max-width: 250px; 
                    height: auto; 
                    display:block; 
                    margin:5px auto; 
                    cursor:pointer; 
                }
            </style>
        """

        self.preview.setHtml(style + html)

    def _update_word_stats(self):
        """
        Update the word and character count label based on the editor content.

        Retrieves the current text from the editor, calculates the number of
        words and characters using the `count_words` helper, and updates
        `self.word_label` to display the counts in the format:
        "Words: X — Chars: Y".
        """
        text = self.content_edit.toPlainText()
        words, chars = count_words(text)
        self.word_label.setText(f"Words: {words} — Chars: {chars}")

    def _insert_image_dialog(self):
        """
        Open a file dialog to select an image, copy it to the local images directory,
        and insert a Markdown image reference into the editor.

        - Opens a QFileDialog to let the user select an image file.
        - Copies the selected file to 'sb_data/images', creating the directory if needed.
        - Inserts a Markdown image tag referencing the copied image at the current
          cursor position in the editor.
        - Triggers a preview update to render the inserted image.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if path:
            dst_dir = Path("sb_data/images")
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / Path(path).name
            shutil.copy(path, dst)

            md = f"\n![image]({dst.as_posix()})\n"
            self.content_edit.insertPlainText(md)
            self._schedule_preview()

    def _bind_shortcuts(self):
        """
        Bind keyboard shortcuts to editor actions for convenience.

        Shortcuts:
        - Ctrl+S: Save the current note.
        - Ctrl+B: Apply bold Markdown formatting to the selected text.
        - Ctrl+I: Apply italic Markdown formatting to the selected text.
        - Ctrl+K: Insert a Markdown link template.
        - F11: Toggle fullscreen mode for the editor.

        Internally, a helper `ks` function is used to create a QAction, set its
        shortcut, connect it to the handler, and add it to the dialog.
        """
        def ks(key, handler):
            act = QAction(self)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(handler)
            self.addAction(act)

        ks("Ctrl+s", self.save_note)
        ks("Ctrl+b", lambda: self.insert_md("**", "**"))
        ks("Ctrl+i", lambda: self.insert_md("_", "_"))
        ks("Ctrl+k", lambda: self.insert_md("[", "](https://)"))
        ks("F11", self._toggle_fullscreen)

    def _add_toolbar_actions(self):
        """
        Initialize and add actions to the editor's toolbar.

        Each action corresponds to a Markdown formatting feature or editor utility:
        - Bold, Italic, Headers (H1-H3)
        - Link insertion, Code Block, Quote, Bullet List
        - Image insertion via file dialog
        - Fullscreen toggle

        Uses a helper function `add` to create text-formatting actions with icons
        and tooltips, connecting them to `insert_md`. Other actions are connected
        to their respective handlers like `_insert_image_dialog` and `_toggle_fullscreen`.
        """
        def add(icon, start, end, tip):
            act = self.toolbar.addAction(QIcon(resource_path(f"resources/icons/{icon}")), "")
            act.setToolTip(tip)
            act.triggered.connect(lambda: self.insert_md(start, end))

        add("bold.png", "**", "**", "Bold")
        add("italic.png", "_", "_", "Italic")
        add("header1.png", "# ", "", "Header")
        add("header2.png", "## ", "", "Header 2")
        add("header3.png", "### ", "", "Header 3")
        add("link.png", "[NAME THE WEBSITE...", "](ALWAYS USE HTTPS://...)", "Link")
        add("code_block.png", "```\n", "\n```", "Code Block")
        add("quote.png", "> ", "", "Quote")
        add("bullet.png", "- ", "", "Bullet List")

        img = self.toolbar.addAction(QIcon(resource_path("resources/icons/insert_image.png")), "Insert Image")
        img.setToolTip("Insert image")
        img.triggered.connect(self._insert_image_dialog)

        fs = self.toolbar.addAction(QIcon(resource_path("resources/icons/full_screen.png")), "")
        fs.setToolTip("Fullscreen (F11)")
        fs.triggered.connect(self._toggle_fullscreen)

    def _toggle_fullscreen(self):
        """
        Toggle the dialog between normal and fullscreen mode.
        """
        if self._is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self._is_fullscreen = not self._is_fullscreen

    def _on_preview_link_clicked(self, url: QUrl):
        url_str = url.toString()

        if url_str.startswith("file:///") and url_str.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            # Local image → open in image viewer
            path = url_str[8:]  # remove 'file:///'
            if os.path.exists(path):
                self._on_preview_img_clicked(path)
        elif url_str.startswith(("http://", "https://")):
            # Web link → open in default browser
            webbrowser.open(url_str)

    def _on_preview_img_clicked(self, path):
        """
        Open an image in a popup dialog when clicked in the preview panel.

        - Opens a QDialog with a QScrollArea to display the image.
        - Scales the image proportionally to fit within 90% of the dialog size.
        - Centers the image in the scrollable area.
        """
        if not os.path.exists(path):
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Scratch Board: Image Viewer")
        dlg.resize(900, 700)

        layout = QVBoxLayout(dlg)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap(path)

        max_width = int(dlg.width() * 0.9)
        max_height = int(dlg.height() * 0.9)
        if pix.width() > max_width or pix.height() > max_height:
            pix = pix.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        lbl.setPixmap(pix)
        scroll.setWidget(lbl)

        dlg.exec()

    def load_stylesheet(self):
        """
        Load the QSS stylesheet for the editor dialog to style widgets consistently.
        """
        try:
            with open(resource_path("ui/themes/editor_view_theme.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load editor_view_theme.qss:", e)
