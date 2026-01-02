from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
)

from utils.custom_context_menu import ContextMenuUtility
from utils.resource_path import resource_path


class ContactsManagerPanel(QDialog):
    """Dialog class for creating or editing a contact."""

    def __init__(
        self,
        parent,
        contact_id=None,
        name="",
        phone="",
        email="",
        website="",
        save_callback=None,
        delete_callback=None,
    ):
        super().__init__(parent)

        self.contact_id = contact_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        # Initialize dialog (window + UI)
        self._setup_window()
        self._build_ui(name, phone, email, website)

    # Window setup
    def _setup_window(self):
        self.setMinimumSize(325, 525)

        if self.contact_id:
            self.setWindowTitle("Scratch Board: Edit Contact")
        else:
            self.setWindowTitle("Scratch Board: New Contact")

    # UI construction
    def _build_ui(self, name, phone, email, website):
        self.layout = QVBoxLayout(self)

        self._add_header_image()
        self._add_inputs(name, phone, email, website)
        self._add_action_buttons()

    def _add_header_image(self):
        image = QLabel()
        image.setPixmap(
            QPixmap(resource_path("resources/icons/astronaut_wave.png"))
        )
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(image)

    def _add_inputs(self, name, phone, email, website):
        self.name_input = self._add_labeled_input(
            "Name:", name, "Name", "Enter a name"
        )
        self.custom_context_menu = ContextMenuUtility(self.name_input)

        self.phone_input = self._add_labeled_input(
            "Phone:", phone, "Phone", "Enter a phone number"
        )
        self.custom_context_menu = ContextMenuUtility(self.phone_input)

        self.email_input = self._add_labeled_input(
            "Email:", email, "N/A", "Enter an email address"
        )
        self.custom_context_menu = ContextMenuUtility(self.email_input)

        self.website_input = self._add_labeled_input(
            "Website:", website, "N/A", "Enter a website address"
        )
        self.custom_context_menu = ContextMenuUtility(self.website_input)

    def _add_labeled_input(self, label, value, placeholder, tooltip):
        self.layout.addWidget(QLabel(label))

        line_edit = QLineEdit(value)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setToolTip(tooltip)

        self.layout.addWidget(line_edit)

        return line_edit

    def _add_action_buttons(self):
        save_btn = self._make_button(
            "Save", "save.png", "Save the contact", self.save
        )
        self.layout.addWidget(save_btn)

        if self.delete_callback:
            delete_btn = self._make_button(
                "Delete", "delete.png", "Delete the contact", self.delete
            )
            self.layout.addWidget(delete_btn)

    @staticmethod
    def _make_button(text, icon_name, tooltip, slot):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setIcon(QIcon(resource_path(f"resources/icons/{icon_name}")))
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet(
            """
            QPushButton {
                text-align: center;
                padding: 4px;
            }
            """
        )
        btn.clicked.connect(slot)
        return btn

    # Actions
    def save(self):
        if self.save_callback:
            self.save_callback(
                self.name_input.text(),
                self.phone_input.text(),
                self.email_input.text(),
                self.website_input.text(),
            )
        self.accept()

    def delete(self):
        if self.delete_callback:
            self.delete_callback()
        self.accept()
