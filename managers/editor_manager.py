import os
import re
import shutil
import webbrowser
from pathlib import Path
from helpers.calc_helpers.count_words import count_words
from helpers.markdown.md_to_html import render_markdown_to_html
from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextBlockFormat, QTextListFormat, QFont
from PySide6.QtWidgets import QFileDialog

class EditorManager:
    IMAGE_DIR = Path("sb_data/images")
    PREVIEW_STYLE = """
        <style>
            body { background: transparent; color: #fff; font-family: sans-serif; }
            img { max-width: 250px; height: auto; display:block; margin:5px auto; cursor:pointer; }
        </style>
    """

    @classmethod
    def load_initial_content(cls, content: str) -> str:
        if not content:
            return ""
        if "<img" in content or "<html" in content:
            return content
        return render_markdown_to_html(content)

    @classmethod
    def prepare_preview(cls, html: str) -> str:
        html = cls._convert_image_paths(html)
        return cls.PREVIEW_STYLE + html

    @staticmethod
    def _convert_image_paths(html: str) -> str:
        def repl(m):
            src = m.group(1)
            abs_path = os.path.abspath(src).replace("\\", "/")
            return f'<a href="file:///{abs_path}"><img src="file:///{abs_path}"></a>'
        return re.sub(r'<img\s+[^>]*src="([^"]+)"[^>]*>', repl, html)

    @classmethod
    def insert_image_via_dialog(cls, parent, cursor) -> bool:
        path, _ = QFileDialog.getOpenFileName(parent, "Insert Image", "",
                                              "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if not path:
            return False

        cls.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        dst = cls.IMAGE_DIR / Path(path).name
        shutil.copy(path, dst)

        cursor.insertHtml(f'<img src="{dst.as_posix()}" style="max-width:250px; height:auto;">')
        return True

    @staticmethod
    def count_words_and_chars(text: str) -> tuple[int, int]:
        return count_words(text)

    # Formatting helpers
    @staticmethod
    def bold(cursor: QTextCursor):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def italic(cursor: QTextCursor):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def header(cursor: QTextCursor, size: int):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        fmt.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(fmt)

    @staticmethod
    def bullet_list(cursor: QTextCursor):
        block_fmt = QTextBlockFormat()
        block_fmt.setIndent(1)
        cursor.mergeBlockFormat(block_fmt)
        cursor.insertList(QTextListFormat.ListDisc)

    # Handle preview links
    @staticmethod
    def handle_preview_link(url_str: str):
        if url_str.startswith("file:///") and url_str.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            path = url_str[8:]
            if os.path.exists(path):
                return ("image", path)
        elif url_str.startswith(("http://", "https://")):
            webbrowser.open(url_str)
        return (None, None)
