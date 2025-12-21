from PySide6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QEvent, Signal

from helpers.ui_helpers.copyable_label import CopyableLabel
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from helpers.ui_helpers.floating_action import FloatingButton


class ContactsView(QWidget):
    """
    The contacts widget displays a searchable, scrollable list of contacts with clickable rows. Includes a floating "Add"
    button and double-click handlers to open the add/edit dialog.

    Signals:
        contact_selected (dict): emitted when a contact is selected (not currently used).
    """
    contact_selected = Signal(dict)  # signal to call elsewhere, maybe but thinking unnecessary

    def __init__(self, categories):
        """
        Initializes the ContactsView.

        Args:
            categories (list): A list of dictionaries, each dictionary representing a contact.
        """
        super().__init__()
        self.categories = categories
        self.all_contacts = []  # store all contacts for filtering

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Search bar setup
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
            QLineEdit:hover {
                border: 1px solid #3498eb;
            }
            QLineEdit:focus {
                border: 1px solid #3498eb;
            }
        """)
        main_layout.addWidget(self.search_bar)

        self.contact_click_handler = None # Store the external click callback

        # Header labels
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        self.column_stretch = [2, 1, 3, 3] # Relative width for columns

        header_labels = ["Name", "Phone", "Email", "Website"]
        for text, stretch in zip(header_labels, self.column_stretch):
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setStyleSheet("color: #B0E0E6; font-size: 14px;")
            #lbl.setFixedWidth(width)
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            #header_layout.addWidget(lbl)
            # Add labels to layout with stretch
            if text == "Name":
                header_layout.addWidget(lbl, 2)
            elif text == "Phone":
                header_layout.addWidget(lbl, 1)
            elif text == "Email":
                header_layout.addWidget(lbl, 3)
            elif text == "Website":
                header_layout.addWidget(lbl, 3)

        #header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scrollable area to hold contact rows
        self.scroll_area = QScrollArea()
        self.scroll_area.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setAlignment(Qt.AlignTop)
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
        """
        Reposition the floating add button on widget resize.
        """
        self.add_btn.reposition()
        super().resizeEvent(event)

    def populate_contacts(self, contacts, on_click=None, store_all=True):
        """
        Populates the contacts widget with a list of contacts within a scroll area.

        Args:
            contacts (list[dict[str, str]]): A list of dictionaries, each dictionary representing a contact.
            on_click (function): A function that will be called when the user clicks on the contact.
            store_all (bool): If True, stores all contacts within a scroll area and used for filtering.
        """
        if store_all:
            self.all_contacts = contacts  # store ONCE when loading full list

        self.contact_click_handler = on_click
        self.list_layout.setSpacing(4)

        contacts = sorted(contacts, key=lambda c: (c["Name"] or "").lower())

        # Clear existing rows
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not contacts:
            # Display empty message iuf no contacts
            empty_contacts = QWidget()
            empty_layout = QVBoxLayout(empty_contacts)
            empty_layout.addStretch()  # top stretch
            empty_label = QLabel("No contacts found.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #aaa; font-size: 16px;")
            empty_layout.addWidget(empty_label)
            empty_layout.addStretch()  # bottom stretch

            self.list_layout.addWidget(empty_contacts)
            return

        for contact in contacts:
            # Create a horizontal row for each contact
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 0, 0, 0)  # remove default margins

            # Name column
            name_label = QLabel(contact["name"] if contact["name"] else "N/A")
            #name_label.setFixedWidth(150)
            name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            name_label.setStyleSheet("color: white; font-weight: bold; padding-left: 2px;")
            name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            name_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(name_label, 2)

            # Phone column
            phone_label = CopyableLabel(contact["phone"] if contact["phone"] else "N/A")
            #phone_label.setFixedWidth(120)
            phone_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            phone_label.setStyleSheet("color: #fff;")
            phone_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            #phone_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(phone_label, 1)

            # Email column
            email_label = QLabel(contact["email"] if contact["email"] else "N/A")
            #email_label.setFixedWidth(180)
            email_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            email_label.setStyleSheet("color: #fff;")
            email_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            email_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(email_label, 3)

            # Website column
            website_label = CopyableLabel(contact["website"] if contact["website"] else "N/A")
            website_label.setTextFormat(Qt.RichText)
            website_label.setStyleSheet("color: #B0E0E6;")
            if contact["website"]:
                website_label.setText(f'<a href="{contact["website"]}" style="color: #B0E0E6; text-decoration: none;">{contact["website"]}</a>')
            else:
                website_label.setText("N/A")
            #website_label.setFixedWidth(200)
            website_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            website_label.setOpenExternalLinks(True)
            website_label.setStyleSheet("color: #B0E0E6")
            website_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            #website_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(website_label, 3)

            #row.addStretch()

            # Wraps the row in a QWidget
            row_widget = QWidget()
            row_widget.setObjectName("row")
            row_widget.setLayout(row)
            row_widget.setMouseTracking(True)
            row_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            row_widget.setFixedHeight(60)
            row_widget.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    padding-left: 0px;
                    padding-right: 6px;
                    padding-bottom: 6px;
                    padding-top: 6px;
                    border-radius: 6px;
                    margin-bottom: 6px;
                }
                QWidget#row {
                    background-color: #333;
                    padding: 6px 6px 6px 0px;
                    border-radius: 4px;
                    border: 0px solid transparent;
                }
                QWidget#row:hover {
                    background-color: #444;
                }
            """)

            # Attach double-click handler
            if on_click:
                def make_handler(c):
                    def handler(event):
                        if event.type() == QEvent.Type.MouseButtonDblClick:
                            on_click(c)
                    return handler
                row_widget.mouseDoubleClickEvent = make_handler(contact)

            self.list_layout.addWidget(row_widget)

    def filter_contacts(self, text):
        """
        Filter contacts based on search text.

        Args:
            text (str): The text to search for in name, phone, email, or website.
        """
        query = text.strip().lower()

        if not query:
            # Show full list again if search is empty
            self.populate_contacts(self.all_contacts, self.contact_click_handler, store_all=False)
            return

        # Filter contacts that match query
        filtered = [
            c for c in self.all_contacts
            if text.lower() in (c["name"] or "").lower()
               or text.lower() in (c["phone"] or "").lower()
               or text.lower() in (c["email"] or "").lower()
               or text.lower() in (c["website"] or "").lower()
        ]

        filtered = sorted(filtered, key=lambda c: (c["name"] or "").lower())

        self.populate_contacts(filtered, self.contact_click_handler, store_all=False)