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

        self.setWindowTitle("Scratch Board: Sticky Note Manager")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)

        # Initialize buttons
        self._initialize_buttons()

        # Load existing notes on startup
        self.load_existing_notes()

    def _initialize_buttons(self):
        """Set up the action buttons."""
        self.new_btn = self._create_button("Add Sticky Note", "resources/icons/sticky_note_btn.png", self.new_note)
        self.refresh_btn = self._create_button("Show All Notes", "resources/icons/refresh_btn.png", self.show_all_notes)

        self.layout.addWidget(self.new_btn)
        self.layout.addWidget(self.refresh_btn)

    def _create_button(self, text, icon_path, callback):
        """Helper function to create buttons."""
        button = QPushButton(text)
        button.setToolTip(text)
        button.setIcon(QIcon(resource_path(icon_path)))
        button.setIconSize(QSize(32, 32))
        button.clicked.connect(callback)
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        button.setMaximumWidth(200)
        button.setMaximumHeight(60)
        return button

    def load_existing_notes(self):
        """Load all sticky notes from the DB and open them automatically."""
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
        """Open all sticky notes from the database."""
        if not self.model:
            return

        notes = self.model.get_notes(category_name="Sticky Notes")
        for note in notes:
            self.open_note(note_id=note["id"], title=note["title"], content=note["content"])
