from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLineEdit, QComboBox, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QEvent, QSize
from helpers.floating_action import FloatingButton
from views.note_card_view import NoteCard
from utils.resource_path import resource_path

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
                background-color: #3498eb;
                border-radius: 30px;
                
            }
            QPushButton#FloatingButton::icon {
                padding-left: 10px;
            }
        """)

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
            empty_notes = QWidget()
            layout = QHBoxLayout(empty_notes)
            layout.setAlignment(Qt.AlignCenter)

            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(resource_path("resources/icons/null.png")).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))

            text_label = QLabel("No notes found.")
            text_label.setStyleSheet("color: white; font-size: 24px;")

            layout.addWidget(icon_label)
            layout.addWidget(text_label)

            self.grid_layout.addWidget(empty_notes, 0, 0)
            return

        cols = 3
        for idx, note in enumerate(notes):
            r, c = divmod(idx, cols)
            card = NoteCard(note, on_click)
            self.grid_layout.addWidget(card, r, c)

