import re
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog,
    QLabel, QLineEdit, QComboBox, QSpinBox, QApplication
)
from PySide6.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QCursor
from PySide6.QtCore import Qt

from ui.fonts.font_list import main_font_list
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.custom_context_menu import ContextMenuUtility
from utils.custom_q_edit import CustomQEdit
from utils.resource_path import resource_path


class NotepadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialization pipeline
        self._setup_window(parent)
        self._build_ui()
        self._connect_signals()

    # Window setup
    def _setup_window(self, parent):
        self.setWindowTitle("Scratch Board: Notepad")
        self.resize(800, 600)

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.center_on_screen(parent)

    # UI construction
    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self._create_text_edit()
        self._create_toolbar()
        self._create_bottom_bar()

    def _create_text_edit(self):
        self.text_edit = CustomQEdit()
        self.text_edit.setPlaceholderText("Start typing a plaintext note...")
        self.text_edit.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.text_edit.setStyleSheet("QTextEdit { font-size: 11pt; }")

        self.main_layout.addWidget(self.text_edit)

        # Override context menu
        self.custom_context_menu = ContextMenuUtility(self.text_edit)

    def _create_toolbar(self):
        toolbar = QHBoxLayout()
        self.main_layout.addLayout(toolbar)

        control_height = 28

        # Font selector
        toolbar.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(main_font_list)
        self.font_combo.setFixedHeight(control_height)
        toolbar.addWidget(self.font_combo)

        # Font size
        toolbar.addWidget(QLabel("Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setFixedHeight(control_height)
        toolbar.addWidget(self.font_size_spin)

        toolbar.addStretch()

        # Count Words + Characters Placeholder
        self.count_label = QLabel("Words: 0 - Chars: 0")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.count_label.setStyleSheet(
            "QLabel { font-size: 10pt; font-family: Segoe UI; }"
        )

        toolbar.addWidget(self.count_label)

    def _create_bottom_bar(self):
        bottom = QHBoxLayout()
        self.main_layout.addLayout(bottom)

        buttons = QHBoxLayout()
        bottom.addLayout(buttons)
        buttons.addStretch()

        self.open_btn = self._make_button("Open", "open.png")
        self.open_btn.setToolTip("Open a plaintext note")

        self.save_btn = self._make_button("Save", "save.png")
        self.save_btn.setToolTip("Save the plaintext note")

        self.clear_btn = self._make_button("Clear", "cancel.png")
        self.clear_btn.setToolTip("Clear the notepad")

        self.undo_btn = self._make_button("Undo", "undo.png")
        self.undo_btn.setToolTip("Undo")

        self.redo_btn = self._make_button("Redo", "redo.png")
        self.redo_btn.setToolTip("Redo")

        for btn in (
            self.open_btn,
            self.save_btn,
            self.clear_btn,
            self.undo_btn,
            self.redo_btn,
        ):
            buttons.addWidget(btn)

        # Buttons on left, search/find on right
        buttons.addStretch(1)

        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.search_input.setMaximumWidth(150)
        bottom.addWidget(self.search_input)

        # Search/find button
        self.search_btn = QPushButton("Find")
        self.search_btn.setIcon(QIcon(resource_path("resources/icons/find.png")))
        bottom.addWidget(self.search_btn)

    @staticmethod
    def _make_button(text, icon_name):
        btn = QPushButton(text)
        btn.setIcon(QIcon(resource_path(f"resources/icons/{icon_name}")))
        return btn

    # Signal connections
    def _connect_signals(self):
        self.font_combo.currentTextChanged.connect(self.update_font)
        self.font_size_spin.valueChanged.connect(self.update_font)

        self.search_btn.clicked.connect(self.search_text)

        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.clear_btn.clicked.connect(self.text_edit.clear)
        self.undo_btn.clicked.connect(self.text_edit.undo)
        self.redo_btn.clicked.connect(self.text_edit.redo)

        self.text_edit.textChanged.connect(self.update_count)

    ### --- Helpers --- ###
    def center_on_screen(self, parent=None):
        self.show()
        if parent:
            self.move(parent.frameGeometry().center() - self.rect().center())
        else:
            screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
            self.move(screen.availableGeometry().center() - self.rect().center())

    def update_font(self):
        font = QFont(self.font_combo.currentText(), self.font_size_spin.value())
        cursor = self.text_edit.textCursor()

        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)
        else:
            self.text_edit.setFont(font)

    def search_text(self):
        query = self.search_input.text()
        if not query:
            return

        cursor = self.text_edit.textCursor()
        found = self.text_edit.document().find(query, cursor)

        if found.isNull():
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            found = self.text_edit.document().find(query, cursor)

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
            self, "Save File", str(notepad_dir),
            "Text Files (*.txt);;All Files (*)"
        )

        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())

    def update_count(self):
        text = self.text_edit.toPlainText()
        words = len([w for w in re.split(r"\s+", text.strip()) if w])
        chars = len(text.replace(" ", "").replace("\n", ""))

        self.count_label.setText(f"Words: {words} - Chars: {chars}")
