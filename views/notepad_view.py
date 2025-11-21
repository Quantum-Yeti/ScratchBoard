from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QFileDialog,
    QLabel, QLineEdit, QComboBox, QSpinBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class NotepadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Notepad")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Text edit area ---
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your notes here...")
        layout.addWidget(self.text_edit)

        # --- Top toolbar: Font and search ---
        toolbar_layout = QHBoxLayout()
        layout.addLayout(toolbar_layout)

        # Font family selector
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Courier New", "Times New Roman", "Verdana", "Consolas"])
        self.font_combo.currentTextChanged.connect(self.update_font)
        toolbar_layout.addWidget(QLabel("Font:"))
        toolbar_layout.addWidget(self.font_combo)

        # Font size selector
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.update_font)
        toolbar_layout.addWidget(QLabel("Size:"))
        toolbar_layout.addWidget(self.font_size_spin)

        toolbar_layout.addStretch()

        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        toolbar_layout.addWidget(self.search_input)
        search_btn = QPushButton("Find")
        search_btn.clicked.connect(self.search_text)
        toolbar_layout.addWidget(search_btn)

        # --- Bottom buttons ---
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_file)
        btn_layout.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_file)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.text_edit.clear)
        btn_layout.addWidget(clear_btn)

        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.text_edit.undo)
        btn_layout.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.text_edit.redo)
        btn_layout.addWidget(redo_btn)

        btn_layout.addStretch()

    # --- Helper methods ---
    def update_font(self):
        font = QFont(self.font_combo.currentText(), self.font_size_spin.value())
        self.text_edit.setFont(font)

    def search_text(self):
        query = self.search_input.text()
        if query:
            cursor = self.text_edit.textCursor()
            document = self.text_edit.document()

            found = document.find(query, cursor)
            if found.isNull():
                # Not found, start from top
                cursor.movePosition(cursor.Start)
                found = document.find(query, cursor)
            if not found.isNull():
                self.text_edit.setTextCursor(found)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text_edit.setPlainText(f.read())

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())
