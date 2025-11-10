from PySide6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QEvent, Signal
from utils.resource_path import resource_path
from helpers.floating_action import FloatingButton


class ContactsView(QWidget):
    contact_selected = Signal(dict)  # Optional signal if you want to handle selection elsewhere

    def __init__(self, categories):
        super().__init__()
        self.categories = categories
        self.all_contacts = []  # store all contacts for filtering

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Search bar
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
            QLineEdit:focus {
                border: 1px solid #3BC7C4;
            }
        """)
        main_layout.addWidget(self.search_bar)

        self.contact_click_handler = None

        # Header labels
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_labels = [("Name", 150), ("Phone", 120), ("Email", 180), ("Website", 200)]
        for text, width in header_labels:
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setStyleSheet("color: #3BC7C4; font-size: 14px;")
            lbl.setFixedWidth(width)
            header_layout.addWidget(lbl)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scrollable area for contact rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(4)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.list_widget)
        main_layout.addWidget(self.scroll_area)

        # Floating add button
        self.add_btn = FloatingButton(
            self,
            icon_path=resource_path("resources/icons/add.png"),
            tooltip="Add contact",
            shortcut="Ctrl+Shift+N"
        )

    def resizeEvent(self, event):
        self.add_btn.reposition()
        super().resizeEvent(event)

    def populate_contacts(self, contacts, on_click=None):
        """Fill the contact list with rows."""
        self.all_contacts = contacts
        self.contact_click_handler = on_click
        self.list_layout.setSpacing(4)

        # Clear existing rows
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not self.all_contacts:
            self.all_contacts = contacts
        if on_click:
            self.contact_click_handler = on_click

        if not contacts:
            empty_label = QLabel("No contacts found.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #aaa; padding: 10px;")
            self.list_layout.addWidget(empty_label)
            return

        for contact in contacts:
            row = QHBoxLayout()
            row.setSpacing(12)

            # Create labels for each column
            name_label = QLabel(contact["name"] if contact["name"] else "N/A")
            name_label.setFixedWidth(150)
            name_label.setStyleSheet("color: white;")
            name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.addWidget(name_label)

            phone_label = QLabel(contact["phone"] if contact["phone"] else "N/A")
            phone_label.setFixedWidth(120)
            phone_label.setStyleSheet("color: #aaa;")
            phone_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.addWidget(phone_label)

            email_label = QLabel(contact["email"] if contact["email"] else "N/A")
            email_label.setFixedWidth(180)
            email_label.setStyleSheet("color: #aaa;")
            email_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.addWidget(email_label)

            website_label = QLabel(contact["website"] if contact["website"] else "N/A")
            website_label.setFixedWidth(200)
            website_label.setStyleSheet("color: #aaa;")
            website_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.addWidget(website_label)

            row.addStretch()

            # Row widget
            row_widget = QWidget()
            row_widget.setLayout(row)
            row_widget.setStyleSheet("""
                QWidget {
                    background-color: #333;
                    padding: 6px;
                    border-radius: 4px;
                }
                QWidget:hover {
                    background-color: #444;
                }
            """)

            # Double click to open
            if on_click:
                def make_handler(c):
                    def handler(event):
                        if event.type() == QEvent.Type.MouseButtonDblClick:
                            on_click(c)
                    return handler
                row_widget.mouseDoubleClickEvent = make_handler(contact)

            self.list_layout.addWidget(row_widget)

    def filter_contacts(self, text):
        """Filter contacts based on search text."""
        if not text.strip():
            # Show full list
            self.populate_contacts(self.all_contacts, self.contact_click_handler)
            return

        filtered = [
            c for c in self.all_contacts
            if text.lower() in (c["name"] or "").lower()
               or text.lower() in (c["phone"] or "").lower()
               or text.lower() in (c["email"] or "").lower()
               or text.lower() in (c["website"] or "").lower()
        ]
        self.populate_contacts(filtered, self.contact_click_handler)
