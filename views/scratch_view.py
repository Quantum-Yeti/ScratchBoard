import random

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QColorDialog
from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
from helpers.ui_helpers.text_color_switcher import get_text_color
from utils.resource_path import resource_path

PASTEL_COLORS = [
    "#BFD8F7",  # Soft Sky Blue
    "#A3CFF7",  # Light Cerulean
    "#89BFF7",  # Powder Blue
    "#97D3E6",  # Muted Cyan
    "#A3D6E8",  # Soft Aqua
    "#B0CFF7",  # Pale Cornflower
    "#A0C8E8",  # Light Steel Blue
    "#B2D8F2",  # Gentle Ice Blue
    "#9EC1E1",  # Frosted Blue
    "#ADD8E6"   # Classic Light Blue
]

class ScratchNote(QDialog):
    RESIZE_MARGIN = 8
    ACTIVE_NOTES = []

    def __init__(self, model, note_id=None, title="Sticky Note", content="", color=None, on_new_note=None):
        super().__init__()
        self.model = model
        self.note_id = note_id
        self.color = color or random.choice(PASTEL_COLORS)
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

        # Note counting
        #self.display_index = len(ScratchNote.ACTIVE_NOTES) + 1
        ScratchNote.ACTIVE_NOTES.append(self)

        #ScratchNote.renumber_scratch_notes()

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

        # Adds a stretch between the title_label and the buttons
        top_bar.addStretch()

        # Add button
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon(resource_path("resources/icons/add_button.png")))
        self.add_button.setIconSize(QSize(24, 24))
        self.add_button.setFixedSize(QSize(30, 30))
        self.add_button.setStyleSheet("background: transparent; border: none;")
        self.add_button.clicked.connect(self.add_new_note)
        top_bar.addWidget(self.add_button)

        # Color Picker Button
        self.color_btn = QPushButton()
        self.color_btn.setIcon(QIcon(resource_path("resources/icons/color_wheel.png")))
        self.color_btn.setIconSize(QSize(24, 24))
        self.color_btn.setFixedSize(30, 30)
        self.color_btn.setStyleSheet("background: transparent; border: none;")
        self.color_btn.clicked.connect(self.pick_color)
        top_bar.addWidget(self.color_btn)

        # Delete Button
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(resource_path("resources/icons/delete_black.png")))
        self.delete_btn.setIconSize(QSize(24, 24))
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("background: transparent; border: none;")
        self.delete_btn.clicked.connect(self.delete_note)
        top_bar.addWidget(self.delete_btn)

        # Close Button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(resource_path("resources/icons/close_black.png")))
        self.close_btn.setIconSize(QSize(24, 24))
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("background: transparent; border: none;")
        self.close_btn.clicked.connect(self.close)
        top_bar.addWidget(self.close_btn)

        # Add top_bar to the layout
        layout.addLayout(top_bar)

        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setText(content)
        self.text_edit.setPlaceholderText("Start typing your sticky note.\nNotes are auto-saved until deleted.")
        layout.addWidget(self.text_edit)

        # Auto-save timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(2000)
        self.dirty = False
        self.text_edit.textChanged.connect(self.mark_dirty)

        self.apply_style()

        # Bottom-right drag/resize icon
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.drag_icon = QLabel()
        self.drag_icon.setPixmap(QIcon(resource_path("resources/icons/drag_box_black.png")).pixmap(22, 22))
        self.drag_icon.setStyleSheet("background: transparent; margin: 0px; padding: 0px;")
        self.drag_icon.setToolTip("Click and drag to resize the note.")
        bottom_bar.addWidget(self.drag_icon, alignment=Qt.AlignRight | Qt.AlignBottom)

        layout.addLayout(bottom_bar)

    def apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.color};
                border: 2px solid #000;  /* No border-radius */
            }}
            QTextEdit {{
                background: {self.color};
                border: 1px solid transparent;
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
        """
            Save the current note's content and title to the database.
            - Retrieves the current text from the note editor.
            - Uses the first line (up to 20 characters) as the note title, or "Sticky Note" if empty.
            - If the note already exists (`self.note_id` is set), updates the existing record.
            - Otherwise, creates a new note entry in the database and assigns its new ID.
            - Updates the window title and visible note title label to match the saved title.
        """
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

    # Dragging and resizing
    def mousePressEvent(self, event):
        """
            Handle mouse press events to initiate dragging or resizing of the window.
            - If the left mouse button is pressed near the bottom-right corner or on the drag icon,
              enables resize mode (`self._resize_active = True`).
            - Otherwise, enables drag mode (`self._drag_active = True`) and stores the offset
              between the mouse position and the top-left corner of the window for smooth dragging.
            - Calls the base class implementation to ensure default event handling.
            Args:
                event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.LeftButton:
            rect = self.rect()
            pos = event.pos()

            # Check if click is on or near the bottom-right corner
            if (
                    pos.x() >= rect.width() - self.RESIZE_MARGIN and
                    pos.y() >= rect.height() - self.RESIZE_MARGIN
            ):
                self._resize_active = True

            # OR if click is on the drag icon
            elif hasattr(self, "drag_icon") and self.drag_icon.geometry().contains(pos):
                self._resize_active = True

            else:
                # Otherwise, treat it as a drag for moving
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
            Handle mouse move events to update dragging, resizing, or cursor appearance.
            - If dragging is active (`self._drag_active`), moves the window following the mouse.
            - If resizing is active (`self._resize_active`), resizes the window based on the mouse position,
              respecting the minimum width and height.
            - If neither drag nor resize is active, updates the cursor to indicate
              a possible resize action when near the bottom-right corner or over the drag icon.
            - Calls the base class implementation to ensure default event handling.
            Args:
                event (QMouseEvent): The mouse move event.
        """
        rect = self.rect()

        if self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

        elif self._resize_active:
            new_width = max(self.minimumWidth(), event.pos().x())
            new_height = max(self.minimumHeight(), event.pos().y())
            self.resize(new_width, new_height)

        else:
            # Change cursor if near bottom-right or over icon
            if (
                    event.pos().x() >= rect.width() - self.RESIZE_MARGIN and
                    event.pos().y() >= rect.height() - self.RESIZE_MARGIN
            ) or (
                    hasattr(self, "drag_icon") and self.drag_icon.geometry().contains(event.pos())
            ):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._resize_active = False
        super().mouseReleaseEvent(event)

    def get_display_title(self):
        """Return a title with a simple note index counter."""
        return "Scratch Note (Sticky Note)"

    def add_new_note(self):
        if callable(self.on_new_note):
            self.on_new_note()

    def pick_color(self):
        new_color = QColorDialog.getColor(QColor(self.color), self, "Select Note Color")
        if not new_color.isValid():
            return

        self.color = new_color.name()
        self.apply_style()
        self.update()
        self.repaint()
        self.mark_dirty()
        self.update_drag_icon()
        self.update_title_color()
        self.update_top_bar_icons()

    def update_drag_icon(self):
        """Switch drag icon depending on brightness of background color."""
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        icon_file = "drag_box_black.png" if brightness > 128 else "drag_box_white.png"
        self.drag_icon.setPixmap(QPixmap(resource_path(f"resources/icons/{icon_file}")))

    def update_title_color(self):
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        text_color = "#000000" if brightness > 150 else "#FFFFFF"

        self.title_label.setStyleSheet(f"""
            background-color: transparent; 
            font-weight: bold; 
            color: {text_color}
        """)

    def update_top_bar_icons(self):
        """
           Update the icons on the note's top bar based on the current background color.
           Determines whether the background color is light or dark, then switches
           the top bar button icons (add, close, color picker, delete) to a version
           that ensures sufficient contrast for visibility.
        """
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        icon_suffix = "_white" if brightness <= 150 else "_black"

        self.add_button.setIcon(QIcon(resource_path(f"resources/icons/add_button{icon_suffix}.png")))
        self.close_btn.setIcon(QIcon(resource_path(f"resources/icons/close{icon_suffix}.png")))
        self.color_btn.setIcon(QIcon(resource_path(f"resources/icons/color_wheel{icon_suffix}.png")))
        self.delete_btn.setIcon(QIcon(resource_path(f"resources/icons/delete{icon_suffix}.png")))

    def delete_note(self):
        """Delete the note from the database"""
        if self.note_id and self.model:
            self.model.delete_note(self.note_id)

        if self in ScratchNote.ACTIVE_NOTES:
            ScratchNote.ACTIVE_NOTES.remove(self)

        self.close()
        #self.renumber_scratch_notes()

    #@staticmethod
    #def renumber_scratch_notes():
        #for i, note in enumerate(ScratchNote.ACTIVE_NOTES, start=1):
            #note.display_index = i
            #if hasattr(note, "title_label"):
                #note.title_label.setText(note.get_display_title())

    def closeEvent(self, event):
        self.auto_save()
        super().closeEvent(event)
