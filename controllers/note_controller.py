import json

from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtWidgets import QMessageBox
from views.editor_view import EditorPanel
from views.widgets.charts_widget import create_stacked_bar_chart, create_multi_line_chart


class NoteController(QObject):
    data_changed = Signal()  # Emitted whenever notes change

    def __init__(self, model, view, sidebar=None):
        super().__init__()  # ensure QObject initialization

        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.current_category = None
        self.search_term = ""
        self.order_by = "updated DESC"

        self.view.add_btn.clicked.connect(self.add_note)

        if hasattr(self.view, "search_input"):
            self.view.search_input.textChanged.connect(self.on_search_changed)

        if self.sidebar is not None:
            self.sidebar.category_selected.connect(self.on_category_changed)

        self.refresh_notes()

    def _notify_change(self):
        """Emit data changed signal separated from UI refresh."""
        self.data_changed.emit()  # Notifies Dashboard
        QTimer.singleShot(0, self.refresh_notes)  # updates list view

    def on_note_click(self, note):
        # Convert JSON string to list
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
        self.search_term = text
        QTimer.singleShot(0, self.refresh_notes)

    def on_category_changed(self, category):
        self.current_category = None if category == "All Categories" else category
        QTimer.singleShot(0, self.refresh_notes)

    def add_note(self):
        def save_cb(title, content, tags=None):
            if not title.strip() and not content.strip():
                QMessageBox.warning(self.view, "Empty Note", "Cannot save an empty note")
                return
            self.model.add_note(self.current_category or "Notes", title, content, tags=tags)
            self._notify_change()  # triggers refresh and dashboard update

        EditorPanel(self.view, None, "New Note", "", save_cb).exec()

    def save_edit(self, note_id, title, content, tags=None):
        self.model.edit_note(note_id, title=title, content=content, tags=tags)
        self._notify_change()

    def delete_note(self, note_id):
        note_to_delete = self.model.get_note_by_id(note_id)
        if not note_to_delete:
            return

        self.model.delete_note(note_id)

        self._notify_change()

    def refresh_notes(self):
        notes = self.model.get_notes(
            category_name=self.current_category,
            search=self.search_term,
            order_by=self.order_by
        )
        self.view.populate_notes(notes, self.on_note_click)