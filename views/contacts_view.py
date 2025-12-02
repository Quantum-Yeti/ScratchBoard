from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QEvent, Signal

from helpers.modules.contacts_copy_menu import CopyableLabel
from utils.resource_path import resource_path
from helpers.ui_helpers.floating_action import FloatingButton


class ContactsView(QWidget):
    contact_selected = Signal(dict)  # signal to call elsewhere, maybe but thinking unnecessary

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
            QLineEdit:hover {
                border: 1px solid #3498eb;
            }
            QLineEdit:focus {
                border: 1px solid #3498eb;
            }
        """)
        main_layout.addWidget(self.search_bar)

        self.contact_click_handler = None

        # Header labels
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        self.column_stretch = [2, 1, 3, 3]

        header_labels = ["Name", "Phone", "Email", "Website"]
        for text, stretch in zip(header_labels, self.column_stretch):
            lbl = QLabel(f"<b>{text}</b>")
            lbl.setStyleSheet("color: #B0E0E6; font-size: 14px;")
            #lbl.setFixedWidth(width)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            #header_layout.addWidget(lbl)

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

        # Scrollable area for contact rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
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
        self.add_btn.reposition()
        super().resizeEvent(event)

    def populate_contacts(self, contacts, on_click=None, store_all=True):
        """Fill the contact list with rows."""
        if store_all:
            self.all_contacts = contacts  # store ONCE when loading full list

        self.contact_click_handler = on_click
        self.list_layout.setSpacing(4)

        # Clear existing rows
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not contacts:
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
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 0, 0, 0)  # remove default margins

            # Create labels for each column
            name_label = QLabel(contact["name"] if contact["name"] else "N/A")
            #name_label.setFixedWidth(150)
            name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            name_label.setStyleSheet("color: white; font-weight: bold; padding-left: 2px;")
            name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            name_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(name_label, 2)

            phone_label = CopyableLabel(contact["phone"] if contact["phone"] else "N/A")
            #phone_label.setFixedWidth(120)
            phone_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            phone_label.setStyleSheet("color: #fff;")
            phone_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            #phone_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(phone_label, 1)

            email_label = QLabel(contact["email"] if contact["email"] else "N/A")
            #email_label.setFixedWidth(180)
            email_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            email_label.setStyleSheet("color: #fff;")
            email_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            email_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(email_label, 3)

            website_label = CopyableLabel()
            website_label.setTextFormat(Qt.RichText)
            website_label.setStyleSheet("color: #B0E0E6;")
            website_label.setText(f'<a href="{contact["website"]}" style="color: #B0E0E6; text-decoration: none;">{contact["website"]}</a>')
            #website_label.setFixedWidth(200)
            website_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            website_label.setOpenExternalLinks(True)
            website_label.setStyleSheet("color: #B0E0E6")
            website_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            #website_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            row.addWidget(website_label, 3)

            #row.addStretch()

            # Row widget
            row_widget = QWidget()
            row_widget.setObjectName("row")
            row_widget.setLayout(row)
            row_widget.setMouseTracking(True)
            row_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
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
        query = text.strip().lower()

        if not query:
            # Show full list again
            self.populate_contacts(self.all_contacts, self.contact_click_handler, store_all=False)
            return

        filtered = [
            c for c in self.all_contacts
            if text.lower() in (c["name"] or "").lower()
               or text.lower() in (c["phone"] or "").lower()
               or text.lower() in (c["email"] or "").lower()
               or text.lower() in (c["website"] or "").lower()
        ]
        self.populate_contacts(filtered, self.contact_click_handler, store_all=False)
