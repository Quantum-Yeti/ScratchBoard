import os
import re
import shutil
import webbrowser
from pathlib import Path
from helpers.calc_helpers.count_words import count_words
from helpers.markdown.md_to_html import render_markdown_to_html
from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextBlockFormat, QTextListFormat, QFont, QColor, Qt
from PySide6.QtWidgets import QFileDialog, QInputDialog, QColorDialog


class EditorManager:
    """Logic class to manage editor panels which includes formatting, preview rendering, and I/O helpers."""

    # Image path for storage
    IMAGE_DIR = Path("sb_data/images")

    # Override CSS/QSS for preview HTML
    PREVIEW_STYLE = """
        <style>
            body { background: transparent; color: #fff; font-family: sans-serif; }
            img { max-width: 250px; height: auto; display:block; margin:5px auto; cursor:pointer; }
        </style>
    """

    @classmethod
    def load_initial_content(cls, content: str) -> str:
        """Normalize editor content (HTML  rather than legacy Markdown)."""
        if not content:
            return ""

        # If already HTML, load
        if "<img" in content or "<html" in content:
            return content

        # Otherwise it's Markdown
        return render_markdown_to_html(content)

    @classmethod
    def prepare_preview(cls, html: str) -> str:
        """Prepare HTML and style for preview."""
        html = cls._convert_image_paths(html)
        return cls.PREVIEW_STYLE + html

    @staticmethod
    def _convert_image_paths(html: str) -> str:
        """Convert image paths (<img> tags) to absolute file path as URL links."""
        def repl(m):
            src = m.group(1)
            abs_path = os.path.abspath(src).replace("\\", "/")
            return f'<a href="file:///{abs_path}"><img src="file:///{abs_path}"></a>'
        return re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', repl, html)

    @classmethod
    def insert_image_via_dialog(cls, parent, cursor) -> bool:
        """Opens a file dialog, copies the image locally into a folder, and inserts the image into the editor."""
        path, _ = QFileDialog.getOpenFileName(parent, "Insert Image", "",
                                              "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if not path:
            return False

        # Make sure image directory exists
        cls.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        dst = cls.IMAGE_DIR / Path(path).name
        shutil.copy(path, dst)

        # Insert the image as HTML
        cursor.insertHtml(f'<img src="{dst.as_posix()}" style="max-width:250px; height:auto;">')
        return True

    @staticmethod
    def count_words_and_chars(text: str) -> tuple[int, int]:
        """Return number of words and characters in text."""
        return count_words(text)

    # Formatting helpers
    @staticmethod
    def bold(cursor: QTextCursor):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def italic(cursor: QTextCursor):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def highlight(cursor: QTextCursor, parent=None):
        """
        Highlight selected text with a user-chosen color.
        """
        if cursor.hasSelection():
            # Open color picker (initial color = light cyan)
            color = QColorDialog.getColor(QColor(102, 255, 255), parent, "Choose Highlight Color")
            if color.isValid():  # user pressed OK
                fmt = QTextCharFormat()
                fmt.setBackground(color)
                cursor.mergeCharFormat(fmt)

    @staticmethod
    def text_color(cursor: QTextCursor, parent=None):
        """
        Let the user select a text color and apply it to the selected text.
        """
        if cursor.hasSelection():
            # Open color picker (initial color = white)
            color = QColorDialog.getColor(QColor(255, 255, 255), parent, "Choose Text Color")
            if color.isValid():  # user pressed OK
                fmt = QTextCharFormat()
                fmt.setForeground(color)
                cursor.mergeCharFormat(fmt)

    @staticmethod
    def header(cursor: QTextCursor, size: int):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def bullet_list(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setIndent(1)
        cursor.mergeBlockFormat(block_fmt)
        cursor.insertList(QTextListFormat.Style.ListDisc)

    @staticmethod
    def numbered_list(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setIndent(1)
        cursor.mergeBlockFormat(block_fmt)
        cursor.insertList(QTextListFormat.Style.ListDecimal)

    @staticmethod
    def align_left(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cursor.mergeBlockFormat(block_fmt)

    @staticmethod
    def align_center(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(block_fmt)

    @staticmethod
    def align_right(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(Qt.AlignmentFlag.AlignRight)
        cursor.mergeBlockFormat(block_fmt)

    @staticmethod
    def insert_hr(cursor: QTextCursor):
        cursor.insertHtml("<hr>")

    # Handle preview links
    @staticmethod
    def handle_preview_link(url_str: str):
        """Handler to manage cliks in the preview (image or external links)."""
        if url_str.startswith("file:///") and url_str.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            path = url_str[8:]
            if os.path.exists(path):
                return "image", path
        elif url_str.startswith(("http://", "https://")):
            webbrowser.open(url_str)
        return None, None

    @staticmethod
    def insert_link(parent, cursor):
        """Insert or edit a rich-text hyperlink."""
        selected_text = cursor.selectedText()

        # Ask for URL
        url, ok = QInputDialog.getText(
            parent,
            "Insert Link",
            "Enter URL:",
            text="https://"
        )
        if not ok or not url.strip():
            return

        # Configures link formatting
        fmt = QTextCharFormat()
        fmt.setAnchor(True)
        fmt.setAnchorHref(url)
        fmt.setFontUnderline(True)
        fmt.setForeground(QColor.fromRgb(138, 180, 248))

        # Apply a link to selection or insert new link text
        if selected_text:
            cursor.mergeCharFormat(fmt)
        else:
            cursor.insertText(url, fmt)
