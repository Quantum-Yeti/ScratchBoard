from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
from views.editor_panel import EditorPanel

class NoteController:
    def __init__(self, model, view, sidebar=None):
        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.current_category = None
        self.search_term = ""
        self.order_by = "updated DESC"

        # Connect add button
        self.view.add_btn.clicked.connect(self.add_note)

        # Connect search input
        if hasattr(self.view, "search_input"):
            self.view.search_input.textChanged.connect(self.on_search_changed)

        # Connect sidebar
        if self.sidebar is not None:
            self.sidebar.category_selected.connect(self.on_category_changed)

        self.refresh_notes()

    def on_note_click(self, note):
        EditorPanel(
            self.view,
            note["title"],
            note["content"],
            lambda t,c: self.save_edit(note["id"], t, c)
        ).exec()

    def on_search_changed(self, text):
        self.search_term = text
        QTimer.singleShot(0, self.refresh_notes)

    def on_category_changed(self, category):
        self.current_category = None if category=="All Categories" else category
        QTimer.singleShot(0, self.refresh_notes)

    def add_note(self):
        def save_cb(title, content):
            if not title.strip() and not content.strip():
                QMessageBox.warning(self.view, "Empty Note", "Cannot save an empty note")
                return
            self.model.add_note(self.current_category or "Notes", title, content)
            QTimer.singleShot(0, self.refresh_notes)
        EditorPanel(self.view, "New Note", "", save_cb).exec()

    def save_edit(self, note_id, title, content):
        self.model.edit_note(note_id, title=title, content=content)
        QTimer.singleShot(0, self.refresh_notes)

    def refresh_notes(self):
        notes = self.model.get_notes(
            category_name=self.current_category,
            search=self.search_term,
            order_by=self.order_by
        )
        self.view.populate_notes(notes, self.on_note_click)
