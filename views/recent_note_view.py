from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtCore import Qt
import markdown2

class RecentNoteView(QWidget):
    def __init__(self, model, open_note_callback):
        super().__init__()
        self.model = model
        self.open_note_callback = open_note_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.title_label = QLabel("Most Recent Note")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        self.preview.setStyleSheet("background: transparent; border: none;")
        self.preview.anchorClicked.connect(self.open_note)
        layout.addWidget(self.preview)

        self.refresh()

    def refresh(self):
        note = self.model.get_most_recent_note()
        if not note:
            self.preview.setHtml("<i>No notes yet...</i>")
            return

        html = markdown2.markdown(
            note["content"], extras=["fenced-code-blocks", "tables"]
        )
        self.preview.setHtml(html)

    def open_note(self, _):
        note = self.model.get_most_recent_note()
        if note:
            self.open_note_callback(note)
