import random
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QColorDialog
from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap, QGuiApplication, QTextCursor, QTextCharFormat

from helpers.ui_helpers.text_color_switcher import get_text_color
from utils.custom_q_edit import CustomQEdit
from utils.resource_path import resource_path

PASTEL_COLORS = [
    "#BFD8F7", "#A3CFF7", "#89BFF7", "#97D3E6", "#A3D6E8",
    "#B0CFF7", "#A0C8E8", "#B2D8F2", "#9EC1E1", "#ADD8E6"
]

class ScratchNote(QDialog):
    """A draggable, snappable, resizable sticky note dialog with autosave and color options."""
    RESIZE_MARGIN = 8
    ACTIVE_NOTES = []
    SNAP_DISTANCE = 20
    UNSNAP_DISTANCE = 35

    def __init__(self, model, note_id=None, title="Sticky Note", content="", color=None, on_new_note=None):
        """Initialize a ScratchNote object."""
        super().__init__()
        self.model = model
        self.note_id = note_id
        self.color = color or random.choice(PASTEL_COLORS)
        self.on_new_note = on_new_note
        self._snap_x = None
        self._snap_y = None
        self._drag_active = False
        self._resize_active = False
        self._drag_pos = QPoint()
        self.dirty = False

        self._init_window(title)
        self._init_layout(content)
        self.apply_style()
        self.set_textedit_color()

        ScratchNote.ACTIVE_NOTES.append(self)

    # Initialization
    def _init_window(self, title):
        """Initialize the window flags, size and title."""
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(300, 200)
        self.resize(450, 350)

    def _init_layout(self, content):
        """Initialize the vertical layout of the window, which includes toolbar, text edit, and bottom drag."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self._init_top_bar(layout)
        self._init_text_edit(layout, content)
        self._init_bottom_bar(layout)

    def _init_top_bar(self, parent_layout):
        """Create the top bar layout with title and buttons."""
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(4, 4, 4, 4)

        # Note title label
        self.title_label = QLabel(self.get_display_title())
        self.title_label.setStyleSheet(f"""
            background-color: transparent;
            font-weight:bold;
            color: {get_text_color(self.color)};
            padding-left: 6px;""")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()

        # Top bar buttons
        self.add_button = self._create_top_button("resources/icons/add_button.png", self.add_new_note)
        self.color_btn = self._create_top_button("resources/icons/color_wheel.png", self.pick_color)
        self.delete_btn = self._create_top_button("resources/icons/delete_black.png", self.delete_note)
        self.close_btn = self._create_top_button("resources/icons/close_black.png", self.close)

        # Add the buttons to the top bar
        for btn in [self.add_button, self.color_btn, self.delete_btn, self.close_btn]:
            top_bar.addWidget(btn)

        parent_layout.addLayout(top_bar)

    def _create_top_button(self, icon_path, callback):
        """This helper creates the top bar button with icon and click callback."""
        btn = QPushButton()
        btn.setIcon(QIcon(resource_path(icon_path)))
        btn.setIconSize(QSize(24, 24))
        btn.setFixedSize(QSize(30, 30))
        btn.setStyleSheet("background: transparent; border: none;")
        btn.clicked.connect(callback)
        return btn

    def _init_text_edit(self, parent_layout, content):
        """Initialize the text edit and autosave timer."""
        self.text_edit = CustomQEdit()
        self.text_edit.setText(content)
        self.text_edit.setPlaceholderText(
            "Start typing your sticky note.\nNotes are auto-saved until deleted."
        )
        self.text_edit.textChanged.connect(self.mark_dirty)
        parent_layout.addWidget(self.text_edit)

        # Autosave every 2 seconds
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(2000)

    def _init_bottom_bar(self, parent_layout):
        """Create the bottom-right drag icon for resizing."""
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.drag_icon = QLabel()
        self.drag_icon.setPixmap(QIcon(resource_path("resources/icons/drag_box_black.png")).pixmap(22, 22))
        self.drag_icon.setStyleSheet("background: transparent; margin: 0px; padding: 0px;")
        self.drag_icon.setToolTip("Click and drag to resize the note.")
        bottom_bar.addWidget(self.drag_icon, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        parent_layout.addLayout(bottom_bar)

    # Styles
    def apply_style(self):
        """Apply background and font color based on note color."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.color};
                border: 2px solid #000;
            }}
            QTextEdit {{
                background: {self.color};
                border: 1px solid transparent;
                font-size: 14px;
                color: {get_text_color(self.color)};
            }}
        """)

    def set_textedit_color(self):
        """Set the text color in CustomQEdit."""
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(get_text_color(self.color)))
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)

    # Note management
    def mark_dirty(self):
        """Mark note as changed (needs to save)."""
        self.dirty = True

    def auto_save(self):
        """Save the note to the database if it is marked dirty."""
        if self.dirty:
            self.save_to_db()
            self.dirty = False

    def save_to_db(self):
        """Save or update the note to the database."""
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

    def add_new_note(self):
        """Callback to add a new note."""
        if callable(self.on_new_note):
            self.on_new_note()

    def delete_note(self):
        """Delete a note from the database and remove from the active list."""
        if self.note_id and self.model:
            self.model.delete_note(self.note_id)
        if self in ScratchNote.ACTIVE_NOTES:
            ScratchNote.ACTIVE_NOTES.remove(self)
        self.close()

    # Color handling
    def pick_color(self):
        """Open color picker and update note color and styles."""
        new_color = QColorDialog.getColor(QColor(self.color), self, "Select Note Color")
        if not new_color.isValid():
            return
        self.color = new_color.name()
        self.apply_style()
        self.set_textedit_color()
        self.update()
        self.repaint()
        self.mark_dirty()
        self.update_drag_icon()
        self.update_title_color()
        self.update_top_bar_icons()

    def update_drag_icon(self):
        """Update the drag icon based on brightness."""
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        icon_file = "drag_box_black.png" if brightness > 128 else "drag_box_white.png"
        self.drag_icon.setPixmap(QPixmap(resource_path(f"resources/icons/{icon_file}")))

    def update_title_color(self):
        """Update the title color based on brightness."""
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        text_color = "#000000" if brightness > 150 else "#FFFFFF"
        self.title_label.setStyleSheet(f"""
            background-color: transparent; 
            font-weight: bold; 
            color: {text_color}
        """)

    def update_top_bar_icons(self):
        """Update the top bar icon based on brightness."""
        c = QColor(self.color)
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        icon_suffix = "_white" if brightness <= 150 else "_black"
        self.add_button.setIcon(QIcon(resource_path(f"resources/icons/add_button{icon_suffix}.png")))
        self.close_btn.setIcon(QIcon(resource_path(f"resources/icons/close{icon_suffix}.png")))
        self.color_btn.setIcon(QIcon(resource_path(f"resources/icons/color_wheel{icon_suffix}.png")))
        self.delete_btn.setIcon(QIcon(resource_path(f"resources/icons/delete{icon_suffix}.png")))

    # Drag & Resize
    def mousePressEvent(self, event):
        """Drag and/or resize based on mouse position."""
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.rect()
            pos = event.pos()
            if (pos.x() >= rect.width() - self.RESIZE_MARGIN and pos.y() >= rect.height() - self.RESIZE_MARGIN) or \
               (hasattr(self, "drag_icon") and self.drag_icon.geometry().contains(pos)):
                self._resize_active = True
            else:
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Move and/or resize while dragging mouse."""
        rect = self.rect()
        if self._drag_active:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            new_pos, snapped = self.snap_to_screen_edges(new_pos)
            new_pos = self.snap_to_other_notes(new_pos)
            self.move(new_pos)
        elif self._resize_active:
            new_width = max(self.minimumWidth(), event.pos().x())
            new_height = max(self.minimumHeight(), event.pos().y())
            self.resize(new_width, new_height)
        else:
            if (event.pos().x() >= rect.width() - self.RESIZE_MARGIN and event.pos().y() >= rect.height() - self.RESIZE_MARGIN) or \
               (hasattr(self, "drag_icon") and self.drag_icon.geometry().contains(event.pos())):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Stoop dragging/resizing when mouse button is released."""
        self._drag_active = False
        self._resize_active = False
        super().mouseReleaseEvent(event)

    # Snap helpers
    def get_screen_geometry(self):
        """Return current screen geometry."""
        center = self.frameGeometry().center()
        screen = QGuiApplication.screenAt(center)
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        return screen.availableGeometry()

    def snap_to_screen_edges(self, pos: QPoint):
        """Snap to screen edges if within SNAP_DISTANCE."""
        snapped = False
        geo = self.get_screen_geometry()
        rect = self.frameGeometry()
        x, y = pos.x(), pos.y()

        # X axis
        if self._snap_x == 'left':
            if abs(x - geo.left()) > self.UNSNAP_DISTANCE:
                self._snap_x = None
            else:
                x = geo.left()
        elif self._snap_x == 'right':
            if abs((x + rect.width()) - geo.right()) > self.UNSNAP_DISTANCE:
                self._snap_x = None
            else:
                x = geo.right() - rect.width()
        else:
            if abs(x - geo.left()) <= self.SNAP_DISTANCE:
                self._snap_x = 'left'
                x = geo.left()
            elif abs((x + rect.width()) - geo.right()) <= self.SNAP_DISTANCE:
                self._snap_x = 'right'
                x = geo.right() - rect.width()

        # Y axis
        if self._snap_y == 'top':
            if abs(y - geo.top()) > self.UNSNAP_DISTANCE:
                self._snap_y = None
            else:
                y = geo.top()
        elif self._snap_y == 'bottom':
            if abs((y + rect.height()) - geo.bottom()) > self.UNSNAP_DISTANCE:
                self._snap_y = None
            else:
                y = geo.bottom() - rect.height()
        else:
            if abs(y - geo.top()) <= self.SNAP_DISTANCE:
                self._snap_y = 'top'
                y = geo.top()
            elif abs((y + rect.height()) - geo.bottom()) <= self.SNAP_DISTANCE:
                self._snap_y = 'bottom'
                y = geo.bottom() - rect.height()

        return QPoint(x, y), snapped

    def snap_to_other_notes(self, pos: QPoint) -> QPoint:
        """Snap to other notes if within SNAP_DISTANCE."""
        rect = self.frameGeometry()
        x, y = pos.x(), pos.y()
        my_left, my_right = x, x + rect.width()
        my_top, my_bottom = y, y + rect.height()

        for note in ScratchNote.ACTIVE_NOTES:
            if note is self:
                continue
            other = note.frameGeometry()
            # Horizontal
            if abs(my_left - other.right()) <= self.SNAP_DISTANCE:
                x = other.right()
            elif abs(my_right - other.left()) <= self.SNAP_DISTANCE:
                x = other.left() - rect.width()
            # Vertical
            if abs(my_top - other.bottom()) <= self.SNAP_DISTANCE:
                y = other.bottom()
            elif abs(my_bottom - other.top()) <= self.SNAP_DISTANCE:
                y = other.top() - rect.height()

        return QPoint(x, y)

    # Misc
    def get_display_title(self):
        """Return display title."""
        return "Scratch Note (Sticky Note)"

    def closeEvent(self, event):
        """Make sure note is autosaved on close."""
        self.auto_save()
        super().closeEvent(event)
