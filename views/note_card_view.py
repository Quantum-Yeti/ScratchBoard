from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtCore import Qt
import markdown
from utils.resource_path import resource_path

class NoteCard(QFrame):
    def __init__(self, note, on_double_click):
        super().__init__()
        self.note = note
        self.on_double_click = on_double_click
        self.setObjectName("NoteCard")

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        title_label = QLabel(note["title"])
        title_label.setObjectName("NoteTitle")
        title_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(title_label)

        # Content (rendered Markdown)
        content_view = QTextBrowser()
        content_view.setOpenExternalLinks(True)
        content_view.setStyleSheet("background: transparent; border: none; a { color: #5DADE2; text-decoration: none;}")
        content_view.setHtml(markdown.markdown(note["content"]))

        # Hide scrollbars but keep original size
        content_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_view.setSizePolicy(
            content_view.sizePolicy().horizontalPolicy(),
            content_view.sizePolicy().verticalPolicy()
        )

        # Content
        layout.addWidget(content_view)

        # Apply stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        """Load external stylesheet for consistent dark theme."""
        try:
            qss_path = resource_path("ui/themes/note_card.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load note_card.qss:", e)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and callable(self.on_double_click):
            self.on_double_click(self.note)
