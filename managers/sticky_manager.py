from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize

from views.sticky_view import ScratchNote
from utils.resource_path import resource_path
import random

PASTEL_COLORS = [
    "#BFD8F7",  # Soft Sky Blue
    "#A3CFF7",  # Light Cerulean
    "#89BFF7",  # Powder Blue
    "#97D3E6",  # Muted Cyan
    "#A3D6E8",  # Soft Aqua
    "#B0CFF7",  # Pale Cornflower
    "#A0C8E8",  # Light Steel Blue
    "#B2D8F2",  # Gentle Ice Blue
    "#9EC1E1",  # Frosted Blue
    "#ADD8E6"   # Classic Light Blue
]

class ScratchManager(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.active_notes = []

        self.setWindowTitle("Sticky Notes")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumWidth(200)
        self.setMinimumHeight(100)
        self.setMaximumWidth(200)
        self.setMaximumHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Add a new scratch note button
        self.new_btn = QPushButton("Add Scratch Note")
        self.new_btn.setToolTip("Add a new scratch note.")
        self.new_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.new_btn.setMaximumWidth(200)
        self.new_btn.setMaximumHeight(60)
        self.new_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;  /* top/bottom, left/right */
            }
        """)
        layout.addWidget(self.new_btn)
        self.new_btn.setIcon(QIcon(resource_path("resources/icons/sticky_note_btn.png")))
        self.new_btn.setIconSize(QSize(32, 32))
        self.new_btn.clicked.connect(self.new_note)

        # Reload all scratch notes from db after they are closed
        self.refresh_btn = QPushButton("Show All Notes")
        self.refresh_btn.setToolTip("Reloads all the scratch notes.")
        self.refresh_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.refresh_btn.setMaximumWidth(200)
        self.refresh_btn.setMaximumHeight(60)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;  /* top/bottom, left/right */
            }
        """)
        self.refresh_btn.setIcon(QIcon(resource_path("resources/icons/refresh_btn.png")))
        self.refresh_btn.setIconSize(QSize(32, 32))
        self.refresh_btn.clicked.connect(self.show_all_notes)

        layout.addWidget(self.new_btn)
        layout.addWidget(self.refresh_btn)

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

    def show_all_notes(self):
        """Reopen all scratch notes from the database."""
        if not self.model:
            return

        self.load_existing_notes()
