from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QColorDialog
from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QColor, QIcon
from utils.resource_path import resource_path

PASTEL_COLORS = ["#FFEBEE", "#FFF3E0", "#E8F5E9", "#E3F2FD", "#F3E5F5"]

def get_text_color(bg_color):
    """Return black or white depending on background brightness."""
    c = QColor(bg_color)
    brightness = (c.red()*299 + c.green()*587 + c.blue()*114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"

class ScratchNote(QDialog):
    RESIZE_MARGIN = 8

    def __init__(self, model, note_id=None, title="Sticky Note", content="", color=None, on_new_note=None):
        super().__init__()
        self.model = model
        self.note_id = note_id
        self.color = color or PASTEL_COLORS[0]
        self.on_new_note = on_new_note

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMinimumSize(300, 200)
        self.resize(450, 350)

        self._drag_active = False
        self._resize_active = False
        self._drag_pos = QPoint()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        # Top bar: delete button with padding
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(4, 4, 4, 4)

        # Sticky note title with index counter
        self.title_label = QLabel(self.get_display_title())
        self.title_label.setStyleSheet(f"""
            background-color: transparent;
            font-weight:bold;
            color: {get_text_color(self.color)};
            padding-left: 6px;""")
        top_bar.addWidget(self.title_label)

        top_bar.addStretch()

        # Add button
        add_button = QPushButton()
        add_button.setIcon(QIcon(resource_path("resources/icons/add_button.png")))
        add_button.setIconSize(QSize(24, 24))
        add_button.setFixedSize(QSize(30, 30))
        add_button.setStyleSheet("background: transparent; border: none;")
        add_button.clicked.connect(self.add_new_note)
        top_bar.addWidget(add_button)

        # Color Picker Button
        color_btn = QPushButton()
        color_btn.setIcon(QIcon(resource_path("resources/icons/color_wheel.png")))
        color_btn.setIconSize(QSize(24, 24))
        color_btn.setFixedSize(30, 30)
        color_btn.setStyleSheet("background: transparent; border: none;")
        color_btn.clicked.connect(self.pick_color)
        top_bar.addWidget(color_btn)

        # Delete from database
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(resource_path("resources/icons/delete_black.png")))
        delete_btn.setIconSize(QSize(24, 24))
        delete_btn.setFixedSize(30, 30)  # slightly bigger clickable area
        delete_btn.setStyleSheet("background: transparent; border: none;")
        delete_btn.clicked.connect(self.delete_note)
        top_bar.addWidget(delete_btn)

        # Close window
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(resource_path("resources/icons/close_black.png")))
        close_btn.setIconSize(QSize(24, 24))
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        layout.addLayout(top_bar)

        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setText(content)
        self.text_edit.setPlaceholderText("Type note...")
        layout.addWidget(self.text_edit)

        # Auto-save timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(2000)
        self.dirty = False
        self.text_edit.textChanged.connect(self.mark_dirty)

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.color};
                border: 2px solid #888;  /* No border-radius */
            }}
            QTextEdit {{
                background: transparent;
                border: none;
                font-size: 14px;
                color: {get_text_color(self.color)};
            }}
        """)

    def mark_dirty(self):
        self.dirty = True

    def auto_save(self):
        if self.dirty:
            self.save_to_db()
            self.dirty = False

    def save_to_db(self):
        text = self.text_edit.toPlainText().strip()
        title = text.split("\n")[0][:20] or "Sticky Note"

        if self.note_id:
            self.model.edit_note(self.note_id, title=title, content=text)
        else:
            self.note_id = self.model.add_note("Sticky Notes", title, text)

        display_title = self.get_display_title()
        self.setWindowTitle(display_title)

        if hasattr(self, "title_label"):
            self.title_label.setText(display_title)

    # --- Dragging and resizing ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = self.rect()
            if event.pos().x() >= rect.width() - self.RESIZE_MARGIN and event.pos().y() >= rect.height() - self.RESIZE_MARGIN:
                self._resize_active = True
            else:
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        elif self._resize_active:
            new_width = max(self.minimumWidth(), event.pos().x())
            new_height = max(self.minimumHeight(), event.pos().y())
            self.resize(new_width, new_height)
        else:
            rect = self.rect()
            if event.pos().x() >= rect.width() - self.RESIZE_MARGIN and event.pos().y() >= rect.height() - self.RESIZE_MARGIN:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._resize_active = False
        super().mouseReleaseEvent(event)

    def get_display_title(self):
        try:
            index = int(self.note_id)
        except (TypeError, ValueError):
            index = ""
        return f"Scratch Note {index}"


    def add_new_note(self):
        if callable(self.on_new_note):
            self.on_new_note()

    def pick_color(self):
        new_color = QColorDialog.getColor(QColor(self.color), self, "Select Note Color")
        if not new_color.isValid():
            return

        self.color = new_color.name()
        self.apply_style()
        self.mark_dirty()

    def delete_note(self):
        """Delete the note from the database"""
        if self.note_id and self.model:
            self.model.delete_note(self.note_id)
        self.close()

    def closeEvent(self, event):
        self.auto_save()
        super().closeEvent(event)
