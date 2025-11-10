from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QEvent
from helpers.floating_action import FloatingButton
from utils.resource_path import resource_path


def load_stylesheet(self):
    try:
        with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())
    except Exception as e:
        print("Failed to load dark_theme.qss:", e)

class ContactsView(QWidget):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        load_stylesheet(self)

        # Scrollable contacts list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(6)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.list_widget)
        layout.addWidget(self.scroll)

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

    def populate_contacts(self, contacts, on_click):
        """Display contacts in a horizontal row style list."""
        # Clear old widgets
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if not contacts:
            empty_label = QLabel("No contacts found.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty_label)
            return

        for contact in contacts:
            row = QHBoxLayout()
            row.setSpacing(12)

            name_label = QLabel(f"<b>{contact['name']}</b>")
            name_label.setStyleSheet("color:white;")
            name_label.setFixedWidth(150)
            row.addWidget(name_label)

            phone_label = QLabel(contact['phone'] or 'N/A')
            phone_label.setFixedWidth(120)
            phone_label.setStyleSheet("color:#aaa;")
            row.addWidget(phone_label)

            email_label = QLabel(contact['email'] or 'N/A')
            email_label.setFixedWidth(180)
            email_label.setStyleSheet("color:#aaa;")
            row.addWidget(email_label)

            website_label = QLabel(contact['website'] or 'N/A')
            website_label.setStyleSheet("color:#aaa;")
            row.addWidget(website_label)

            # Make the whole row clickable
            row_widget = QWidget()
            row_widget.setLayout(row)
            row_widget.setStyleSheet("background-color:#333; padding:6px; border-radius:4px;")

            # Double click to open
            def double_click_handler(c):
                def handler(event):
                    if event.type() == QEvent.Type.MouseButtonDblClick:
                        on_click(c)
                return handler
            row_widget.mouseDoubleClickEvent = double_click_handler(contact)

            self.list_layout.addWidget(row_widget)
