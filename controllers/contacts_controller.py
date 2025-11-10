from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QMessageBox
from views.contacts_editor_view import ContactEditorPanel  # Create similar to EditorPanel for contacts

class ContactsController(QObject):
    def __init__(self, model, view, sidebar=None):
        super().__init__()
        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.current_category = None

        # Connect add button
        self.view.add_btn.clicked.connect(self.add_contact)

        # Connect category selection from sidebar
        if self.sidebar is not None:
            self.sidebar.category_selected.connect(self.on_category_changed)

        self.refresh_contacts()

    def _notify_change(self):
        QTimer.singleShot(0, self.refresh_contacts)

    def on_contact_click(self, contact):
        """Open editor for editing/deleting contact"""
        ContactEditorPanel(
            parent=self.view,
            contact_id=contact["id"],
            name=contact["name"],
            phone=contact["phone"],
            email=contact["email"],
            website=contact["website"],
            save_callback=lambda n, p, e, w: self.save_edit(contact["id"], n, p, e, w),
            delete_callback=lambda cid=contact["id"]: self.delete_contact(cid)
        ).exec()

    def on_category_changed(self, category):
        self.current_category = None if category == "All Categories" else category
        QTimer.singleShot(0, self.refresh_contacts)

    def add_contact(self):
        """Open editor panel to add a new contact"""
        def save_cb(name, phone, email, website):
            if not name.strip():
                QMessageBox.warning(self.view, "Empty Contact", "Name cannot be empty")
                return
            self.model.add_contact(self.current_category or "Contacts", name, phone, website, email)
            self._notify_change()

        ContactEditorPanel(self.view, None, "", "", "", "", save_cb).exec()

    def save_edit(self, contact_id, name, phone, email, website):
        self.model.edit_contact(contact_id, name, phone, website, email)
        self._notify_change()

    def delete_contact(self, contact_id):
        self.model.delete_contact(contact_id)
        self._notify_change()

    def refresh_contacts(self):
        contacts = self.model.get_contacts(category_name=self.current_category)
        self.view.populate_contacts(contacts, self.on_contact_click)
