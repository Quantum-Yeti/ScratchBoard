from PySide6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QSizePolicy, QFrame, QBoxLayout
)
from PySide6.QtCore import Qt, QEvent, Signal

from helpers.ui_helpers.copyable_label import CopyableLabel
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from helpers.ui_helpers.floating_action import FloatingButton


class ContactsView(QWidget):
    """Displays a searchable, scrollable list of contacts with a floating add button."""
    LEFT_MARGIN = 5
    RIGHT_MARGIN = 5
    COLUMN_SPACING = 12

    contact_selected = Signal(dict)

    def __init__(self, categories):
        super().__init__()

        self.categories = categories
        self.all_contacts = []
        self.contact_click_handler = None

        # Initialize UI
        self._build_layout()
        self._create_search_bar()
        self._create_contact_list()
        self._create_header_row() # Add header as first row in the list
        self._create_floating_button()

    # UI construction
    def _build_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)

    def _create_search_bar(self):
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search contacts...")
        self.search_bar.textChanged.connect(self.filter_contacts)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #222;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #555;
            }
            QLineEdit:hover,
            QLineEdit:focus {
                border: 1px solid #3498eb;
            }
        """)
        self.main_layout.addWidget(self.search_bar)

    def _create_contact_list(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.list_widget)
        self.main_layout.addWidget(self.scroll_area)

    def _create_header_row(self):
        """Create the top header row inside the list layout"""
        self.header_container = QWidget()
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setSpacing(self.COLUMN_SPACING)
        header_layout.setContentsMargins(self.LEFT_MARGIN, 0, self.RIGHT_MARGIN, 0)
        header_layout.setDirection(QBoxLayout.Direction.LeftToRight)

        headers = [
            ("Name", 2),
            ("Phone", 2),
            ("Email", 2),
            ("Website", 2),
        ]

        for text, stretch in headers:
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setStyleSheet("color: #B0E0E6; font-size: 14px;")
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            header_layout.addWidget(lbl, stretch)

        self.header_container.setFixedHeight(30)
        self.header_container.setStyleSheet("""
            QWidget {
                background-color: #222;
                border-bottom: 0px solid #555;
            }
        """)

        # Insert header as the first item in the list layout
        if hasattr(self, "list_layout"):
            self.list_layout.insertWidget(0, self.header_container)
        else:
            self.main_layout.addWidget(self.header_container)

    def _create_floating_button(self):
        self.add_btn = FloatingButton(
            self,
            icon_path=resource_path("resources/icons/add.png"),
            tooltip="Add contact",
            shortcut="Ctrl+Shift+N",
        )

    # Events
    def resizeEvent(self, event):
        self.add_btn.reposition()
        super().resizeEvent(event)

    # Contact population
    def populate_contacts(self, contacts, on_click=None, store_all=True):
        if store_all:
            self.all_contacts = contacts

        self.contact_click_handler = on_click
        self.list_layout.setSpacing(4)

        contacts = sorted(contacts, key=lambda c: (c["name"] or "").lower())
        self._clear_contacts(keep_header=True)

        if not contacts:
            self._show_empty_state()
            return

        for contact in contacts:
            self.list_layout.addWidget(self._create_contact_row(contact, on_click))

    def _clear_contacts(self, keep_header=False):
        """Clear all contact rows but keep the header row"""
        start_index = 1 if keep_header else 0
        while self.list_layout.count() > start_index:
            item = self.list_layout.takeAt(start_index)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _show_empty_state(self):
        empty = QWidget()
        layout = QVBoxLayout(empty)
        layout.addStretch()

        label = QLabel("No contacts found.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #aaa; font-size: 16px;")

        layout.addWidget(label)
        layout.addStretch()

        self.list_layout.addWidget(empty)

    def _create_contact_row(self, contact, on_click):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(self.COLUMN_SPACING)
        row_layout.setContentsMargins(self.LEFT_MARGIN, 0, self.RIGHT_MARGIN, 0)
        row_layout.setDirection(QBoxLayout.Direction.LeftToRight)

        # Column order must match headers: Name, Phone, Email, Website
        row_layout.addWidget(self._make_label(contact["name"], bold=True), 2)
        row_layout.addWidget(self._make_label(contact["phone"] or "N/A"), 2)
        row_layout.addWidget(self._make_label(contact["email"]), 2)
        row_layout.addWidget(self._make_website_label(contact["website"]), 2)

        row_widget = QWidget()
        row_widget.setObjectName("row")
        row_widget.setLayout(row_layout)
        row_widget.setFixedHeight(60)
        row_widget.setContentsMargins(0, 0, 0, 0)
        row_widget.setStyleSheet("""
            QWidget { background-color: transparent; }
            QWidget#row {
                background-color: #333;
                padding: 6px 0px;
                border-radius: 8px;
                margin-bottom: 4px;
            }
            QWidget#row:hover {
                background-color: #444;
            }
        """)

        # Optional double-click handler
        if on_click:
            def handler(event, c=contact):
                if event.type() == QEvent.Type.MouseButtonDblClick:
                    on_click(c)

            row_widget.mouseDoubleClickEvent = handler

        return row_widget

    # Helpers
    @staticmethod
    def _make_label(text, bold=False):
        lbl = QLabel(text or "N/A")
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setStyleSheet("color: white; font-weight: bold;" if bold else "color: white;")
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        return lbl

    @staticmethod
    def _make_email_label(email):
        lbl = QLabel(email or "N/A")
        lbl.setOpenExternalLinks(False)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl.setStyleSheet("color: #B0E0E6")
        return lbl

    @staticmethod
    def _make_website_label(website):
        lbl = QLabel(website or "N/A")
        lbl.setOpenExternalLinks(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        lbl.setStyleSheet("color: #B0E0E6")
        return lbl

    # Filtering
    def filter_contacts(self, text):
        query = text.strip().lower()

        if not query:
            self.populate_contacts(self.all_contacts, self.contact_click_handler, store_all=False)
            return

        filtered = [
            c for c in self.all_contacts
            if query in (c["name"] or "").lower()
            or query in (c["phone"] or "").lower()
            or query in (c["email"] or "").lower()
            or query in (c["website"] or "").lower()
        ]

        filtered = sorted(filtered, key=lambda c: (c["name"] or "").lower())
        self.populate_contacts(filtered, self.contact_click_handler, store_all=False)
