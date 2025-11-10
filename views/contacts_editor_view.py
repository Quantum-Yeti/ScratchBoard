from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

class ContactEditorPanel(QDialog):
    def __init__(self, parent, contact_id=None, name="", phone="", email="", website="", save_callback=None, delete_callback=None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.save_callback = save_callback
        self.delete_callback = delete_callback

        # Set window titles
        if contact_id:
            self.setWindowTitle("Edit Contact")
        else:
            self.setWindowTitle("New Contact")

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        self.phone_input = QLineEdit(phone)
        self.phone_input.setPlaceholderText("Phone")
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)

        self.email_input = QLineEdit(email)
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        self.website_input = QLineEdit(website)
        self.website_input.setPlaceholderText("Website")
        layout.addWidget(QLabel("Website:"))
        layout.addWidget(self.website_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        if delete_callback:
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(self.delete)
            layout.addWidget(delete_btn)

    def save(self):
        if self.save_callback:
            self.save_callback(
                self.name_input.text(),
                self.phone_input.text(),
                self.email_input.text(),
                self.website_input.text()
            )
        self.accept()

    def delete(self):
        if self.delete_callback:
            self.delete_callback()
        self.accept()
