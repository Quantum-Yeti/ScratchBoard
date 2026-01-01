from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout

from utils.custom_context_menu import ContextMenuUtility
from views.widgets.reference_widget import ReferenceWidget


class ReferencePopup(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Custom Links")
        self.resize(500, 700)

        # Allow minimizing / close independently
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)  # Non-blocking

        layout = QVBoxLayout(self)

        # Embed your existing widget inside the dialog
        self.ref_view = ReferenceWidget(model)
        layout.addWidget(self.ref_view)

        self.custom_context_menu = ContextMenuUtility(self.ref_view)