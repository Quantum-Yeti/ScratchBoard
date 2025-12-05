import json

from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtWidgets import QMessageBox
from views.editor_view import EditorPanel

class NoteController(QObject):
    """
    Controller for the Note model.

    Responsibilities:
    - Retrieve notes from storage and populate the UI
    - Handle note creation, editing, and deleting
    - Filter results by category or search query
    - Notify other views such as dashboard charts when note data changes
    """
    data_changed = Signal()  # Emitted whenever notes change

    def __init__(self, model, view, sidebar=None):
        """
        Constructor to initialize the controller for the notes view.

        :param model: database operations
        :param view: UI component displaying notes in list
        :param sidebar: Emits category filter selections
        """
        super().__init__()

        self.model = model
        self.view = view
        self.sidebar = sidebar

        # Active filters
        self.current_category = None
        self.search_term = ""
        self.order_by = "updated DESC"

        # Connect add note button to new note action
        self.view.add_btn.clicked.connect(self.add_note)

        # Connect search field if something is typed in it
        if hasattr(self.view, "search_input"):
            self.view.search_input.textChanged.connect(self.on_search_changed)

        # Connect category selection from sidebar
        if self.sidebar is not None:
            self.sidebar.category_selected.connect(self.on_category_changed)

        # Initializes loading all notes for UI
        self.refresh_notes()

    def _notify_change(self):
        """
        Notify other views such as dashboard charts when note data changes and refreshes the displayed notes list.

        QTimer is used to schedule UI update after current event cycle.
        """
        self.data_changed.emit()  # Notifies Dashboard
        QTimer.singleShot(0, self.refresh_notes)  # updates list view

    def on_note_click(self, note):
        """
        Opens the editor dialog to modify, save, or delete a selected note.

        :param note: A single note entry from database query
        """
        # Convert JSON string to Python list for adding tags
        tags = json.loads(note["tags"]) if note["tags"] else []

        EditorPanel(
            parent=self.view,
            note_id=note["id"],
            title=note["title"],
            content=note["content"],
            save_callback=lambda t, c, tags=None: self.save_edit(note["id"], t, c, tags),
            delete_callback=lambda nid=note["id"]: self.delete_note(nid),
            tags=tags
        ).exec()

    def on_search_changed(self, text):
        """
        Update the search filter and refresh results.
        """
        self.search_term = text
        QTimer.singleShot(0, self.refresh_notes)

    def on_category_changed(self, category):
        """
        Updates the active category filter from sidebar selection.
        """
        # Set None when showing all notes
        self.current_category = None if category == "All Categories" else category
        QTimer.singleShot(0, self.refresh_notes)

    def add_note(self):
        """
        Open an empty editor dialog to create a new note.
        Prevents saving an empty note.
        """
        def save_cb(title, content, tags=None):
            # Validation to avoid saving blank notes
            if not title.strip() and not content.strip():
                QMessageBox.warning(self.view, "Empty Note", "Cannot save an empty note")
                return

            # If no category selected, go to default view
            self.model.add_note(self.current_category or "Notes", title, content, tags=tags)
            self._notify_change()  # triggers refresh and dashboard update

        EditorPanel(self.view, None, "New Note", "", save_cb).exec()

    def save_edit(self, note_id, title, content, tags=None):
        """
        Save modification to an existing note.
        :param note_id: ID of the note to save modification in the SQLite database.
        """
        self.model.edit_note(note_id, title=title, content=content, tags=tags)
        self._notify_change()

    def delete_note(self, note_id):
        """
        Delete a note and refresh UI.

        :param note_id: SQLite database ID of the note to delete.
        """
        # Retrieve latest data before deletion
        note_to_delete = self.model.get_note_by_id(note_id)
        if not note_to_delete:
            return # Ensures no operation if record is already gone

        self.model.delete_note(note_id)
        self._notify_change()

    def refresh_notes(self):
        """
        Queries and displays notes by filters on the notes list UI.
        """
        notes = self.model.get_notes(
            category_name=self.current_category,
            search=self.search_term,
            order_by=self.order_by
        )
        self.view.populate_notes(notes, self.on_note_click)