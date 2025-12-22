import re
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QFileDialog,
    QLabel, QLineEdit, QComboBox, QSpinBox, QApplication
)
from PySide6.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QCursor
from PySide6.QtCore import Qt

from ui.fonts.font_list import main_font_list
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path

class NotepadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Notepad")
        #self.setModal(False)
        self.resize(800, 600)

        # Allow to minimize and close
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.NonModal)

        self.center_on_screen(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Text edit area
        self.text_edit = QTextEdit()
        self.text_edit.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 10pt;
            }
        """)
        self.text_edit.setPlaceholderText("Type your notes here...")
        layout.addWidget(self.text_edit)

        # Top toolbar: Font and search
        toolbar_layout = QHBoxLayout()
        layout.addLayout(toolbar_layout)

        # Desired uniform height for controls
        control_height = 28  # adjust as needed

        # Font family selector
        self.font_combo = QComboBox()
        self.font_combo.addItems(main_font_list)
        self.font_combo.setFixedHeight(control_height)
        self.font_combo.currentTextChanged.connect(self.update_font)
        font_label = QLabel("Font:")
        font_label.setFixedHeight(control_height)
        toolbar_layout.addWidget(font_label)
        toolbar_layout.addWidget(self.font_combo)

        # Font size selector
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setFixedHeight(control_height)
        self.font_size_spin.valueChanged.connect(self.update_font)
        size_label = QLabel("Size:")
        size_label.setFixedHeight(control_height)
        toolbar_layout.addWidget(size_label)
        toolbar_layout.addWidget(self.font_size_spin)

        toolbar_layout.addStretch()

        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        toolbar_layout.addWidget(self.search_input)

        # Find/search button
        search_btn = QPushButton("Find")
        search_btn.setIcon(QIcon(resource_path("resources/icons/find.png")))
        search_btn.clicked.connect(self.search_text)
        toolbar_layout.addWidget(search_btn)


        # Bottom buttons
        bottom_layout = QHBoxLayout()
        layout.addLayout(bottom_layout)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.setIcon(QIcon(resource_path("resources/icons/open.png")))
        open_btn.clicked.connect(self.open_file)
        btn_layout.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon(resource_path("resources/icons/save.png")))
        save_btn.clicked.connect(self.save_file)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setIcon(QIcon(resource_path("resources/icons/cancel.png")))
        clear_btn.clicked.connect(self.text_edit.clear)
        btn_layout.addWidget(clear_btn)

        undo_btn = QPushButton("Undo")
        undo_btn.setIcon(QIcon(resource_path("resources/icons/undo.png")))
        undo_btn.clicked.connect(self.text_edit.undo)
        btn_layout.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.setIcon(QIcon(resource_path("resources/icons/redo.png")))
        redo_btn.clicked.connect(self.text_edit.redo)
        btn_layout.addWidget(redo_btn)

        bottom_layout.addLayout(btn_layout)
        btn_layout.addStretch()

        # Word/char count
        self.count_label = QLabel("Words: 0 - Chars: 0")
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                font-family: Segoe UI;
            }
        """)
        self.count_label.setAlignment(Qt.AlignVCenter)
        self.text_edit.textChanged.connect(self.update_count)
        bottom_layout.addWidget(self.count_label)

    # Helper methods
    def center_on_screen(self, parent=None):
        """Centers the dialog on the parent window if available, else on the current screen."""
        self.show()  # must show to get correct size
        if parent:
            parent_geom = parent.frameGeometry()
            parent_center = parent_geom.center()
            self.move(parent_center - self.rect().center())
        else:
            screen = QApplication.screenAt(QCursor.pos())
            if not screen:
                screen = QApplication.primaryScreen()
            screen_geom = screen.availableGeometry()
            self.move(screen_geom.center() - self.rect().center())

    def update_font(self):
        font = QFont(self.font_combo.currentText(), self.font_size_spin.value())
        cursor = self.text_edit.textCursor()

        if cursor.hasSelection():
            # Applies font change to only selected text
            font_change = QTextCharFormat()
            font_change.setFont(font)
            cursor.mergeCharFormat(font_change)
        else:
            # Default to changing the entire text if nothing selected
            self.text_edit.setFont(font)

    def search_text(self):
        query = self.search_input.text()
        if query:
            cursor = self.text_edit.textCursor()
            document = self.text_edit.document()

            found = document.find(query, cursor)
            if found.isNull():
                # Not found, start from top
                cursor.movePosition(QTextCursor.MoveOperation.Start)
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
        notepad_dir = Path("sb_data/notepad")
        notepad_dir.mkdir(parents=True, exist_ok=True)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            str(notepad_dir),  # 👈 default starting folder
            "Text Files (*.txt);;All Files (*)"
        )

        if not path:
            return



        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text_edit.toPlainText())

    def update_count(self):
        text = self.text_edit.toPlainText()

        # Count words: split by any whitespace sequence
        words = len([w for w in re.split(r'\s+', text.strip()) if w])

        # Count characters excluding whitespace
        chars = len(text.replace(" ", "").replace("\n", ""))

        self.count_label.setText(f"Words: {words} - Chars: {chars}")



