from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt


class ScratchPad(QDialog):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Pad")
        self.resize(600, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.model = model

        layout = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Mapping from QTextEdit to note ID
        self.tab_note_map = {}

        # Controls for tabs
        tab_btn_layout = QHBoxLayout()
        self.new_tab_btn = QPushButton("New Tab")
        self.new_tab_btn.clicked.connect(self.add_tab)
        self.save_tab_btn = QPushButton("Save Tab")
        self.save_tab_btn.clicked.connect(self.save_current_tab)
        self.close_tab_btn = QPushButton("Close Tab")
        self.close_tab_btn.clicked.connect(self.close_current_tab)
        tab_btn_layout.addWidget(self.new_tab_btn)
        tab_btn_layout.addWidget(self.save_tab_btn)
        tab_btn_layout.addWidget(self.close_tab_btn)
        tab_btn_layout.addStretch()
        layout.addLayout(tab_btn_layout)

        # Load existing scratch notes
        self.reload_tabs()

        # Start with one tab if none exist
        if self.tabs.count() == 0:
            self.add_tab()

    def reload_tabs(self):
        """Clear current tabs and reload all scratch notes from DB."""
        self.tabs.clear()
        self.tab_note_map.clear()

        if not self.model:
            return

        notes = self.model.get_notes(category_name="Scratch Notes", order_by="created ASC")
        for note in notes:
            self.add_tab(title=note["title"], content=note["content"], note_id=note["id"])

    def add_tab(self, title=None, content="", note_id=None):
        """Add a new tab. If note_id provided, link to DB note."""
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Write your scratch note here...")
        text_edit.setText(content)
        tab_title = title if title else f"Untitled {self.tabs.count() + 1}"
        self.tabs.addTab(text_edit, tab_title)
        self.tabs.setCurrentWidget(text_edit)

        if self.model:
            if note_id:
                self.tab_note_map[text_edit] = note_id
            else:
                # Auto-create a note in DB immediately for new tabs
                new_id = self.model.add_note("Scratch Notes", tab_title, content)
                self.tab_note_map[text_edit] = new_id

    def save_current_tab(self):
        widget = self.tabs.currentWidget()
        if widget:
            self.save_tab(widget)
            QMessageBox.information(self, "Saved", "Scratch note saved!")

    def save_tab(self, widget):
        """Save a specific tab to DB."""
        if not widget or not self.model:
            return
        text = widget.toPlainText().strip()
        if not text:
            return

        title_index = self.tabs.indexOf(widget)
        title = self.tabs.tabText(title_index)
        note_id = self.tab_note_map.get(widget)

        if note_id:
            self.model.edit_note(note_id, title=title, content=text)
        else:
            new_id = self.model.add_note("Scratch Notes", title, text)
            self.tab_note_map[widget] = new_id

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            widget = self.tabs.widget(current_index)
            confirm = QMessageBox.question(
                self,
                "Close Tab?",
                "Are you sure you want to close this tab? Unsaved content will be saved automatically.",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.save_tab(widget)
                self.tab_note_map.pop(widget, None)
                self.tabs.removeTab(current_index)

    def closeEvent(self, event):
        """Autosave all tabs on close."""
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            self.save_tab(widget)
        super().closeEvent(event)

    def showEvent(self, event):
        """Reload all tabs whenever ScratchPad is shown."""
        super().showEvent(event)
        self.reload_tabs()
