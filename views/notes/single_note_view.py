import base64
from io import BytesIO

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextBrowser, QMenu
from PySide6.QtCore import Qt, QEvent, Signal
import markdown

from helpers.ui_helpers.image_pop import ImagePopup
from ui.themes.context_menu_theme import menu_style
from utils.resource_path import resource_path


def show_context_menu(widget, pos):
    """Show a dark-themed context menu with hover color."""
    menu = QMenu(widget)
    menu.setStyleSheet(menu_style)  # your dark + hover blue style

    # Convert local pos to global coordinates
    global_pos = widget.mapToGlobal(pos)
    menu.exec_(global_pos)


class NoteCard(QFrame):
    """
    A visual card representing a single note with title and rendered Markdown content.
    Supports double-clicking anywhere on the card (*not the content) to trigger a callback.
    """

    # Emit signal for image right click
    imgRightClicked = Signal(str)

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
        self.content_view = QTextBrowser()
        self.content_view.setOpenExternalLinks(True)
        self.content_view.setStyleSheet(
            "background: none; border: none; a { color: #5DADE2; text-decoration: none;}"
        )

        self.content_view.setMouseTracking(True)
        self.content_view.viewport().setMouseTracking(True)
        self.content_view.viewport().installEventFilter(self)

        # Override context menu events on right click
        self.content_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.content_view.customContextMenuRequested.connect(
            lambda pos: show_context_menu(self.content_view, pos)
        )

        # Render markdown to HTML
        rendered_markdown = markdown.markdown(self.note["content"])

        # Optional cached image appended below text
        img_html = ""
        cached = getattr(self.note, "_cached_pix", None)
        img_path = getattr(self.note, "image_path", None)
        if cached:
            # inline encode ONCE
            buffer = BytesIO()
            cached.save(buffer, "PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            img_html = f'<br><img src="data:image/png;base64,{encoded}" data-path="{img_path}" />'

        # Combine everything with your styling
        html = f"""
            <style>
                a {{
                    color: #5dade2;
                    text-decoration: none;
                }}
                img {{
                    max-width: 180px;
                    height: auto;
                    border-radius: 6px;
                    cursor: pointer;
                }}
            </style>
            {rendered_markdown}
            {img_html}
        """
        self.content_view.setHtml(html)

        # Hide scrollbars but keep original size
        self.content_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content_view.setSizePolicy(
            self.content_view.sizePolicy().horizontalPolicy(),
            self.content_view.sizePolicy().verticalPolicy()
        )

        # Make sure double-click anywhere works within the box, does not work on text, links, or image_helpers
        for child in self.findChildren(QTextBrowser) + self.findChildren(QLabel):
            child.installEventFilter(self)

        # Connect right-clicked image signal to helper popup
        #self.imgRightClicked.connect(lambda path: ImagePopup.show(self, path))

        # Add content view to layout
        layout.addWidget(self.content_view)

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
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if callable(self.on_double_click):
                self.on_double_click(self.note)
            return True

        if obj == self.content_view.viewport():
            if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.RightButton:
                cursor = self.content_view.cursorForPosition(event.pos())
                fmt = cursor.charFormat()
                if fmt.isImageFormat():
                    # Try to get image path from HTML attribute
                    img_path = fmt.toImageFormat().name()
                    self.imgRightClicked.emit(img_path)
                    return True

        return super().eventFilter(obj, event)

