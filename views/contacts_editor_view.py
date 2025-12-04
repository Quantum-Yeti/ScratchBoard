from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

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
            self.setWindowTitle("Edit Contact")
        else:
            self.setWindowTitle("New Contact")

        # Main vertical layout
        layout = QVBoxLayout(self)

        # Name input
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        # Phone input
        self.phone_input = QLineEdit(phone)
        self.phone_input.setPlaceholderText("Phone")
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)

        # Email input
        self.email_input = QLineEdit(email)
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        # Website input
        self.website_input = QLineEdit(website)
        self.website_input.setPlaceholderText("Website")
        layout.addWidget(QLabel("Website:"))
        layout.addWidget(self.website_input)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        # Delete button called if editing
        if delete_callback:
            delete_btn = QPushButton("Delete")
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
