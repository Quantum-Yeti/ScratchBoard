from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QTabWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt

class ScratchPad(QDialog):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Pad")
        self.resize(500, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.model = model

        layout = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Counter for unique tab names
        self.tab_counter = 0

        # Controls for tabs
        tab_btn_layout = QHBoxLayout()
        self.new_tab_btn = QPushButton("New Tab")
        self.new_tab_btn.clicked.connect(lambda: self.add_tab())  # ignore signal arg
        self.save_tab_btn = QPushButton("Save Tab")
        self.save_tab_btn.clicked.connect(self.save_current_tab)
        self.close_tab_btn = QPushButton("Close Tab")
        self.close_tab_btn.clicked.connect(self.close_current_tab)
        tab_btn_layout.addWidget(self.new_tab_btn)
        tab_btn_layout.addWidget(self.save_tab_btn)
        tab_btn_layout.addWidget(self.close_tab_btn)
        tab_btn_layout.addStretch()
        layout.addLayout(tab_btn_layout)

        # Start with one tab
        self.add_tab()

    def add_tab(self, title=None, *args):
        """Add a new tab with unique title."""
        self.tab_counter += 1
        if title is None:
            title = f"Untitled {self.tab_counter}"
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Write your scratch note here...")
        self.tabs.addTab(text_edit, str(title))
        self.tabs.setCurrentWidget(text_edit)

    def save_current_tab(self):
        widget = self.tabs.currentWidget()
        if not widget:
            return
        text = widget.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Empty Note", "Cannot save an empty note.")
            return
        # Save to database if model is provided
        if self.model:
            self.model.add_note("Scratch Notes", "Quick Note", text)
        QMessageBox.information(self, "Saved", "Scratch note saved!")

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            confirm = QMessageBox.question(
                self,
                "Close Tab?",
                "Are you sure you want to close this tab? Unsaved content will be lost.",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.tabs.removeTab(current_index)
