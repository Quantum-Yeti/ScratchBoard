import os
import random

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, \
    QPushButton, QSizePolicy, QCompleter
from PySide6.QtCore import Qt, QSize, QThread, Signal, QStringListModel

from helpers.ui_helpers.empty_messages import empty_messages
from helpers.ui_helpers.floating_action import FloatingButton
from helpers.ui_helpers.image_pop import ImagePopup
from models.note_model import NoteModel
from ui.themes.floating_action_style import floating_btn_style
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from views.notes.single_note_view import NoteCard

class PopulateNotesThread(QThread):
    """
    Background thread for preparing note images.

    Scales and caches note images off the UI thread, then emits
    the processed notes back to the main thread.
    """

    thread_loaded = Signal(list, object) # notes + click handler

    def __init__(self, notes, on_click, max_size=250):
        super().__init__()
        self.notes = notes
        self.on_click = on_click
        self.max_size = max_size

    def run(self):
        """Process note images and cache scaled pixmaps."""
        # Image cache once
        for note in self.notes:
            # If we already processed this note before, skip work entirely
            if hasattr(note, "_cached_pix"):
                continue

            img_path = getattr(note, "image_path", None)
            if img_path and os.path.exists(img_path):
                pix = QPixmap(img_path)

                # Scale image to a thumbnail size
                if pix.width() > self.max_size or pix.height() > self.max_size:
                    pix = pix.scaled(
                        self.max_size,
                        self.max_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )

                # Cache the pixmap on the note object
                note._cached_pix = pix

        # Notifies the main thread
        self.thread_loaded.emit(self.notes, self.on_click)

class MainNotesView(QWidget):
    """
    Main notes view widget.

    Displays notes in a scrollable grid or list layout, supports
    searching, and provides a floating action button for adding notes.
    """

    def __init__(self, categories):
        super().__init__()

        # Track thread and state
        self.note_model = NoteModel()
        self._thread = None
        self._last_click = None
        self._last_notes = None
        self.categories = categories

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top control bar (Search + View Toggle)
        controls_layout = QHBoxLayout()

        # Create a QStringListModel to feed to QCompleter
        self.completer_model = QStringListModel()

        # Create the completer
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes…")
        self.search_input.setCompleter(self.completer)  # attach completer
        controls_layout.addWidget(self.search_input)

        self.search_input.textChanged.connect(self.on_text_changed)

        # Toggle button for grid and list view
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

        # Floating add note button
        self.add_btn = FloatingButton(self,
                                      icon_path="resources/icons/add.png",
                                      tooltip="Add note",
                                      shortcut="Ctrl+N")
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

    def populate_notes_async(self, notes, on_click):
        """
        Populate notes in a background thread safely.

        If a previous populate thread is still running, it will be
        terminated cleanly before starting a new one, this avoids thread races.
        """
        self._last_notes = notes
        self._last_click = on_click

        # Stop any running thread
        if hasattr(self, "_thread") and self._thread is not None:
            if self._thread.isRunning():
                self._thread.quit()
                self._thread.wait()

        # Create a new thread and keep a reference
        self._thread = PopulateNotesThread(notes, on_click)
        self._thread.thread_loaded.connect(self._populate_notes_from_thread)
        self._thread.start()

    def _populate_notes_from_thread(self, notes, on_click):
        """ Called in main thread to safely populate the grid."""
        self.populate_notes(notes, on_click)

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

        # Empty state - no notes
        if not notes:
            empty_notes = QWidget()
            main_layout = QVBoxLayout(empty_notes)

            # Layout
            main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            main_layout.setContentsMargins(20, 10, 20, 40)
            main_layout.setSpacing(16)

            # Astronaut icon
            icon_label = QLabel()
            pixmap = QPixmap(resource_path("resources/icons/splash.png"))
            pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            main_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

            # Empty message labels
            text_label = QLabel(random.choice(empty_messages))
            text_label.setStyleSheet("""
                color: white;
                font-size: 20px;
                font-weight: bold;
                font-style: italic;
            """)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setWordWrap(True)
            text_label.setSizePolicy(text_label.sizePolicy().horizontalPolicy(),
                                     text_label.sizePolicy().verticalPolicy())

            main_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignHCenter)

            # Make the empty_notes widget expand to fill the scroll area
            empty_notes.setSizePolicy(
                self.scroll.sizePolicy().horizontalPolicy(),
                self.scroll.sizePolicy().verticalPolicy()
            )

            # Wrap in a container to center inside scroll area
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.addStretch(1)  # top spacer
            container_layout.addWidget(empty_notes, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addStretch(1)  # bottom spacer

            self.grid_layout.addWidget(container, 0, 0, 1, -1)
            return

        # Grid view
        if self.view_mode == "grid":
            cols = 3

            # This will stretch columns equally when toggling grid -> list; list -> grid
            for i in range(cols):
                self.grid_layout.setColumnStretch(i, 1)
            self.grid_layout.setColumnStretch(cols, 0)

            for idx, note in enumerate(notes):
                r, c = divmod(idx, cols)
                card = NoteCard(note, on_click)

                # Image popup helper, right-click
                card.imgRightClicked.connect(lambda path, parent=self: ImagePopup.show(parent, path))

                # Resets styles for grid when toggling
                card.setMinimumHeight(0)
                self.scroll.setMaximumHeight(16777215)
                card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                self.grid_layout.addWidget(card, r, c)
            self.grid_layout.setContentsMargins(8,8,8,8)

        # List View
        else:
            # Force single column stretching
            for i in range(self.grid_layout.columnCount()):
                self.grid_layout.setColumnStretch(i, 0)
            self.grid_layout.setColumnStretch(0, 1)

            card_height = None

            for row, note in enumerate(notes):
                card = NoteCard(note, on_click)

                # Connecting right-click on image for image dialog
                card.imgRightClicked.connect(lambda path, parent=self: ImagePopup.show(parent, path))

                # Forcing card to list row
                card.setMinimumHeight(0)
                card.setMaximumWidth(16777215)
                card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                self.grid_layout.addWidget(card, row, 0, 1, -1)

                # Get height of the first card
                if row == 0:
                    card_height = card.sizeHint().height()

            if card_height:
                spacing = self.grid_layout.spacing()
                max_height = (card_height * 3) + (spacing * 2)
                self.scroll.setMaximumHeight(max_height)


        # Force UI refresh
        self.grid_widget.adjustSize()
        self.scroll.updateGeometry()

    def toggle_view_mode(self):
        """Toggle between grid and list layouts."""
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

    # Trie-based Suggestions
    def on_text_changed(self, text):
        suggestions = self.note_model.autocomplete(text)
        self.completer_model.setStringList(suggestions)
        if suggestions:
            self.completer.complete(self.search_input.rect())



