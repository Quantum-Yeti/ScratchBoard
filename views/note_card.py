from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextBrowser
import markdown
from utils.resource_path import resource_path

class NoteCard(QFrame):
    def __init__(self, note, on_click):
        super().__init__()
        self.note = note
        self.on_click = on_click
        self.setObjectName("NoteCard")

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        title_label = QLabel(note["title"])
        title_label.setObjectName("NoteTitle")
        layout.addWidget(title_label)

        content_view = QTextBrowser()
        content_view.setOpenExternalLinks(True)
        content_view.setStyleSheet("background: transparent; border: none;")
        content_view.setHtml(markdown.markdown(note["content"]))
        layout.addWidget(content_view)

    def mousePressEvent(self, event):
        if callable(self.on_click):
            self.on_click(self.note)
