from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from views.scratch_view import ScratchNote
from utils.resource_path import resource_path
import random

PASTEL_COLORS = ["#FFEBEE", "#FFF3E0", "#E8F5E9", "#E3F2FD", "#F3E5F5"]

class ScratchManager(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.active_notes = []

        self.setWindowTitle("Sticky Notes")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(200)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.new_btn = QPushButton("New Sticky Note")
        self.new_btn.clicked.connect(self.new_note)
        layout.addWidget(self.new_btn)

        self.load_existing_notes()

    def load_existing_notes(self):
        """Load all sticky notes from the DB and open them."""
        if not self.model:
            return

        notes = self.model.get_notes(category_name="Sticky Notes")
        for note in notes:
            color = note["color"] if note["color"] else random.choice(PASTEL_COLORS)
            self.open_note(note_id=note["id"], title=note["title"], content=note["content"], color=color)

    def open_note(self, note_id=None, title="Sticky Note", content="", color=None):
        """Open a single ScratchNote window."""
        color = color or random.choice(PASTEL_COLORS)
        note = ScratchNote(self.model, note_id=note_id, title=title, content=content, color=color, on_new_note=self.new_note)
        note.show()
        self.active_notes.append(note)

    def new_note(self):
        """Create a new sticky note and open it."""
        color = random.choice(PASTEL_COLORS)
        self.open_note(title="New Note", content="", color=color)
