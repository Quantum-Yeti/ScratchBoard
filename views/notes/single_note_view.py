from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextBrowser
from PySide6.QtCore import Qt, QEvent
import markdown

from ui.menus.context_menu import ModifyContextMenu
from utils.resource_path import resource_path

class NoteCard(QFrame):
    """
    A visual card representing a single note with title and rendered Markdown content.
    Supports double-clicking anywhere on the card (*not the content) to trigger a callback.
    """

    def __init__(self, note, on_double_click):
        """
        Initialize a NoteCard.
        Args:
            note (dict): A dictionary containing note data, must have "title" and "content".
            on_double_click (callable): Callback function invoked when the card is double-clicked.
        """
        super().__init__()
        self.note = note
        self.on_double_click = on_double_click
        self.setObjectName("NoteCard")

        # Main vertical layout for title and content
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title label
        title_label = QLabel(note["title"])
        title_label.setObjectName("NoteTitle")
        title_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(title_label)

        # Content area (rendered Markdown)
        content_view = QTextBrowser()
        content_view.setOpenExternalLinks(True)
        content_view.setStyleSheet(
            "background: transparent; border: none; a { color: #5DADE2; text-decoration: none;}"
        )

        # Apply the menu_style for context menus
        self.context_menu = ModifyContextMenu()

        # Override context menu events on right click
        content_view.setContextMenuPolicy(Qt.CustomContextMenu)
        content_view.customContextMenuRequested.connect(
            lambda pos: self.context_menu.contextMenuEvent(content_view)
        )

        # Render Markdown content to HTML
        html = markdown.markdown(self.note["content"])
        html = f"""
        <style>
        a {{
            color: #5dade2;
            text-decoration: none;
        }}
        </style>
        {html}
        """
        content_view.setHtml(html)

        # Hide scrollbars but keep original size
        content_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_view.setSizePolicy(
            content_view.sizePolicy().horizontalPolicy(),
            content_view.sizePolicy().verticalPolicy()
        )

        # Make sure double-click anywhere works within the box, does not work on text, links, or image_helpers
        for child in self.findChildren(QTextBrowser) + self.findChildren(QLabel):
            child.installEventFilter(self)

        # Add content view to layout
        layout.addWidget(content_view)

        # Apply stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        """Load the external stylesheet for consistent dark theme styling."""
        try:
            qss_path = resource_path("ui/themes/note_card_theme.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load note_card_theme.qss:", e)

    def mouseDoubleClickEvent(self, event):
        """
        Handle double-clicks on the card itself.
        Args:
            event (QMouseEvent): The mouse event triggering the double click.
        """
        if event.button() == Qt.LeftButton and callable(self.on_double_click):
            self.on_double_click(self.note)

    def eventFilter(self, obj, event):
        """
        Filter child events to catch double-clicks on labels or QTextBrowser content.
        Args:
            obj (QObject): The child object where the event occurred.
            event (QEvent): The event to filter.
        Returns:
            bool: True if the event was handled, otherwise False.
        """
        if event.type() == QEvent.MouseButtonDblClick:
            if callable(self.on_double_click):
                self.on_double_click(self.note)
            return True  # stop further handling
        return super().eventFilter(obj, event)
