from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLineEdit, QComboBox, QLabel
from PySide6.QtCore import Qt, QEvent
from helpers.floating_action import FloatingButton
from views.note_card_view import NoteCard

class MainView(QWidget):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search + Category filter
        controls_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        controls_layout.addWidget(self.search_input)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)
        controls_layout.addWidget(self.category_filter)
        layout.addLayout(controls_layout)

        # Scrollable notes grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0,0,0,0)
        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)

        # Floating add button
        self.add_btn = FloatingButton(self, icon_path="resources/icons/edit.png", tooltip="Add note", shortcut="Ctrl+N")

    def resizeEvent(self, event):
        self.add_btn.reposition()
        super().resizeEvent(event)

    def populate_notes(self, notes, on_click):
        """Display notes in a grid safely."""
        if not hasattr(self, "grid_layout") or self.grid_layout is None:
            return  # layout destroyed

        # Remove all child widgets but keep the layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)  # detach safely
                widget.deleteLater()

        if not notes:
            empty_label = QLabel("No notes found.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0)
            return

        cols = 3
        for idx, note in enumerate(notes):
            r, c = divmod(idx, cols)
            card = NoteCard(note, on_click)
            self.grid_layout.addWidget(card, r, c)

