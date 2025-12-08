import random

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, \
    QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize

from helpers.ui_helpers.empty_messages import empty_messages
from helpers.ui_helpers.floating_action import FloatingButton
from ui.themes.floating_action_style import floating_btn_style
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from views.notes.single_note_view import NoteCard


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
        self._last_click = None
        self._last_notes = None
        self.categories = categories

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top control bar (Search + View Toggle)
        controls_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes…")
        controls_layout.addWidget(self.search_input)

        # Toggle button
        self.toggle_view_btn = QPushButton()
        self.toggle_view_btn.setIcon(QIcon(resource_path("resources/icons/list.png")))
        self.toggle_view_btn.setIconSize(QSize(24, 24))
        #self.toggle_view_btn.setFixedWidth(40)
        self.toggle_view_btn.setToolTip("Toggle list / grid view")
        self.toggle_view_btn.clicked.connect(self.toggle_view_mode)
        controls_layout.addWidget(self.toggle_view_btn)

        layout.addLayout(controls_layout)

        # Scrollable notes grid
        self.view_mode = "grid"
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet("border: none;")
        self.scroll.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
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
        self.setStyleSheet(floating_btn_style)

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
        self._last_notes = notes
        self._last_click = on_click

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

            # Layout tuning
            main_layout.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
            main_layout.setContentsMargins(20, 40, 20, 40)
            main_layout.setSpacing(16)

            # Astronaut icon
            icon_label = QLabel()
            pixmap = QPixmap(resource_path("resources/icons/owl_empty.png"))
            pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)

            main_layout.addWidget(icon_label, alignment=Qt.AlignHCenter)

            # Text message
            text_label = QLabel(random.choice(empty_messages))
            text_label.setStyleSheet("""
                color: white;
                font-size: 20px;
                font-weight: bold;
                font-style: italic;
            """)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)
            text_label.setSizePolicy(text_label.sizePolicy().horizontalPolicy(),
                                     text_label.sizePolicy().verticalPolicy())

            main_layout.addWidget(text_label, alignment=Qt.AlignHCenter)

            # Make the empty_notes widget expand to fill the scroll area
            empty_notes.setSizePolicy(
                self.scroll.sizePolicy().horizontalPolicy(),
                self.scroll.sizePolicy().verticalPolicy()
            )

            # Wrap in a container to center inside scroll area
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addStretch(1)  # top spacer
            container_layout.addWidget(empty_notes, alignment=Qt.AlignCenter)
            container_layout.addStretch(1)  # bottom spacer

            self.grid_layout.addWidget(container, 0, 0, 1, -1)
            return

        if self.view_mode == "grid":
            cols = 3

            # This will stretch columns equally when toggling grid -> list; list -> grid
            for i in range(cols):
                self.grid_layout.setColumnStretch(i, 1)
            self.grid_layout.setColumnStretch(cols, 0)

            for idx, note in enumerate(notes):
                r, c = divmod(idx, cols)
                card = NoteCard(note, on_click)

                # Resets styles for grid when toggling
                card.setMinimumHeight(0)
                card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                self.grid_layout.addWidget(card, r, c)
            self.grid_layout.setContentsMargins(8,8,8,8)

        else:  # LIST VIEW
            # Force single column stretching
            for i in range(self.grid_layout.columnCount()):
                self.grid_layout.setColumnStretch(i, 0)
            self.grid_layout.setColumnStretch(0, 1)

            for row, note in enumerate(notes):
                card = NoteCard(note, on_click)

                # Forcing card to list row
                card.setMinimumHeight(0)
                card.setMaximumWidth(16777215)
                card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                self.grid_layout.addWidget(card, row, 0, 1, -1)

        # Force UI refresh
        self.grid_widget.adjustSize()
        self.scroll.updateGeometry()

    def toggle_view_mode(self):
        if self.view_mode == "grid":
            self.view_mode = "list"
            self.toggle_view_btn.setIcon(QIcon(resource_path("resources/icons/grid.png")))
            self.toggle_view_btn.setIconSize(QSize(24, 24))
        else:
            self.view_mode = "grid"
            self.toggle_view_btn.setIcon(QIcon(resource_path("resources/icons/list.png")))
            self.toggle_view_btn.setIconSize(QSize(24, 24))

        # Re-populate if notes loaded
        if hasattr(self, "_last_notes") and hasattr(self, "_last_click"):
            self.populate_notes(self._last_notes, self._last_click)
