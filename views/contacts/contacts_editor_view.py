from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

from utils.resource_path import resource_path

class ContactEditorPanel(QDialog):
    """
    ContactEditorPanel QDialog class is used for creating and editing a contact within ContactsView.

    Provides input fields for name, phone, email, and website, along with a save and delete button.

    Args:
        parent (QWidget): Parent widget for this application.
        contact_id: Unique contact ID.
        name (str): Contact name.
        phone (str): Contact phone.
        email (str): Contact email.
        website (str): Contact website.
        save_callback (callable): Function that will be called when a contact is saved.
        delete_callback (callable): Function that will be called when a contact is deleted.
    """
    def __init__(self, parent, contact_id=None, name="", phone="", email="", website="", save_callback=None, delete_callback=None):
        """
        Initialize the ContactEditorPanel class.
        """
        super().__init__(parent)
        self.contact_id = contact_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        # Set window title depending on editing or creating a contact.
        if contact_id:
            self.setWindowTitle("Scratch Board: Edit Contact")
            self.setMinimumSize(325, 525)
        else:
            self.setWindowTitle("Scratch Board: New Contact")
            self.setMinimumSize(325, 525)

        # Main vertical layout
        layout = QVBoxLayout(self)

        # Top image
        self.image = QLabel()
        self.image.setPixmap(QPixmap(resource_path("resources/icons/astronaut_wave.png")))
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image)

        # Name input
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Name")
        self.name_input.setToolTip("Enter a name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        # Phone input
        self.phone_input = QLineEdit(phone)
        self.phone_input.setPlaceholderText("Phone")
        self.phone_input.setToolTip("Enter a phone number")
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)

        # Email input
        self.email_input = QLineEdit(email)
        self.email_input.setPlaceholderText("Email")
        self.email_input.setToolTip("Enter an email address")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # Website input
        self.website_input = QLineEdit(website)
        self.website_input.setPlaceholderText("Website")
        self.website_input.setToolTip("Enter a website address")
        layout.addWidget(QLabel("Website:"))
        layout.addWidget(self.website_input)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save the contact")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.setIconSize(QSize(24, 24))
        save_btn.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 4px;
            }
        """)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        # Delete button called if editing
        if delete_callback:
            delete_btn = QPushButton("Delete")
            delete_btn.setToolTip("Delete the contact")
            delete_btn.setIcon(QIcon(resource_path("resources/icons/delete.png")))
            delete_btn.setIconSize(QSize(24, 24))
            delete_btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 4px;
                }
            """)
            delete_btn.clicked.connect(self.delete)
            layout.addWidget(delete_btn)

    def save(self):
        """
        Collect values from input fields and call the save callback.
        Dialog closes thereafter.
        """
        if self.save_callback:
            self.save_callback(
                self.name_input.text(),
                self.phone_input.text(),
                self.email_input.text(),
                self.website_input.text()
            )
        self.accept()

    def delete(self):
        """
        Call the delete callback if provided and close the dialog.
        """
        if self.delete_callback:
            self.delete_callback()
        self.accept()
