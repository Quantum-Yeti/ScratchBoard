from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Qt
from helpers.ui_helpers.floating_action import FloatingButton
from utils.resource_path import resource_path
from views.note_card_view import NoteCard


class MainView(QWidget):
    """
    Main notes view widget.

    Provides a searchable, scrollable grid of note cards along with a
    floating action button for creating new notes. Handles layout
    initialization, category filtering, and dynamic population of the
    note grid.
    """

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
        self.add_btn = FloatingButton(self, icon_path="resources/icons/add.png", tooltip="Add note", shortcut="Ctrl+N")
        self.add_btn.setIconSize(self.size() * 0.6)  # 60% of button size
        self.setStyleSheet("""
            QPushButton#FloatingButton {
                border: none;
                border-radius: 30px;
            }
            QPushButton#FloatingButton:hover {
                background-color: #3498eb;
            }
            QPushButton#FloatingButton::icon {
                padding-left: 10px;
            }
        """)

    def resizeEvent(self, event):
        """
        Repositions the floating action button on window resize.

        Ensures the button remains anchored in its intended location
        whenever the view is resized.
        """
        self.add_btn.reposition()
        super().resizeEvent(event)

    def populate_notes(self, notes, on_click):
        """
        Populate the notes grid with note cards. If note card category
        is empty, an empty-state message is displayed.
        """
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
            empty_notes = QWidget()
            main_layout = QVBoxLayout(empty_notes)
            main_layout.setAlignment(Qt.AlignCenter)
            main_layout.setSpacing(12)

            # Astronaut icon
            icon_label = QLabel()
            pixmap = QPixmap(resource_path("resources/icons/astronaut_splash.png"))

            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(icon_label)

            # Text message
            text_label = QLabel("No notes found.\nAdd a note using MarkDown or PlainText.")
            text_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-style: italic;")
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)
            main_layout.addWidget(text_label)

            # Make the empty_notes widget expand to fill the scroll area
            empty_notes.setSizePolicy(
                self.scroll.sizePolicy().horizontalPolicy(),
                self.scroll.sizePolicy().verticalPolicy()
            )

            # Wrap in a container to center inside scroll area
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addStretch()  # top spacer
            container_layout.addWidget(empty_notes, alignment=Qt.AlignCenter)
            container_layout.addStretch()  # bottom spacer

            self.grid_layout.addWidget(container, 0, 0, 1, -1)
            return

        cols = 3
        for idx, note in enumerate(notes):
            r, c = divmod(idx, cols)
            card = NoteCard(note, on_click)
            self.grid_layout.addWidget(card, r, c)

