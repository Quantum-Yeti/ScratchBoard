from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout


def open_widget_in_dialog(parent, widget, title="Popout"):
    # Store original parent & layout
    original_parent = widget.parent()
    original_layout = original_parent.layout() if original_parent else None
    original_index = None

    # Find widget index in its layout
    if original_layout:
        for i in range(original_layout.count()):
            if original_layout.itemAt(i).widget() is widget:
                original_index = i
                break

    # Hide the widget in place
    widget.hide()

    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumSize(500, 500)
    dialog.setWindowFlag(Qt.WindowStaysOnTopHint)

    layout = QVBoxLayout(dialog)
    layout.addWidget(widget)
    widget.show()  # show in dialog

    # Restore after dialog closes
    def restore():
        widget.setParent(original_parent)
        if original_layout and original_index is not None:
            original_layout.insertWidget(original_index, widget)
        widget.show()

    dialog.finished.connect(restore)
    dialog.show()