from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QMessageBox
from views.contacts_editor_view import ContactEditorPanel  # Create similar to EditorPanel for contacts

class ContactsController(QObject):
    """
    Controller class for the contacts view.

    Handles interactions between the contacts model and view:
    - Loads contact entries from the SQLite database
    - Adds new contacts to the database
    - Deletes contacts from the database
    - Updates contacts model
    - Listens for sidebar category changes
    - Refreshes UI when data changes
    """
    def __init__(self, model, view, sidebar=None):
        """
        Initialize the ContactsController.
        :param model: Data access layer for contact storage (SQLite)
        :param view: UI component responsible for displaying contact entries
        :param sidebar: Sidebar component responsible for displaying sidebar category changes
        """
        super().__init__()
        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.current_category = None

        # Connect add button to contact creation handler
        self.view.add_btn.clicked.connect(self.add_contact)

        # Category selection event -> trigger UI refresh
        if self.sidebar is not None:
            self.sidebar.category_selected.connect(self.on_category_changed)

        # Initial population of contacts into UI
        self.refresh_contacts()

    def _notify_change(self):
        """
        Trigger a UI refresh after data mutation.
        QTimer ensures refresh occurs after current event loop finishes.
        """
        QTimer.singleShot(0, self.refresh_contacts)

    def on_contact_click(self, contact):
        """
        Open the editor dialog to modify or delete a contact.

        :param contact: Contact data dictionary with keys.
        """
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
        """
        Update the active category when the sidebar changes.

        :param category: Name of selected category or all categories.
        """
        # None = no filter
        self.current_category = None if category == "All Categories" else category

        # Refresh UI on next loop
        QTimer.singleShot(0, self.refresh_contacts)

    def add_contact(self):
        """
        Opens the editor dialog to add a new contact.
        Validates that a name and email were entered before saving.
        """
        def save_cb(name, phone, email, website):
            # Prevents empty name and email
            if not name.strip():
                QMessageBox.warning(self.view, "Empty Contact", "Name cannot be empty")
                return
            if not phone.strip():
                QMessageBox.warning(self.view, "Empty Contact", "Email cannot be empty")
                return

            # Default to the main contacts category for all contacts if no category selected
            self.model.add_contact(self.current_category or "Contacts", name, phone, website, email)
            self._notify_change()

        # None + empty strings -> new contact
        ContactEditorPanel(self.view, None, "", "", "", "", save_cb).exec()

    def save_edit(self, contact_id, name, phone, email, website):
        """
        Save a modification to an existing contact.

        :param contact_id: Unique contact ID.
        """
        self.model.edit_contact(contact_id, name, phone, website, email)
        self._notify_change()

    def delete_contact(self, contact_id):
        """
        Delete a contact and refresh UI.

        :param contact_id: ID of the contact to delete.
        """
        self.model.delete_contact(contact_id)
        self._notify_change()

    def refresh_contacts(self):
        """
        Pull latest contacts from the SQLite database model, filter by active category, and refresh UI.
        """
        contacts = self.model.get_contacts(category_name=self.current_category)
        self.view.populate_contacts(contacts, self.on_contact_click)
