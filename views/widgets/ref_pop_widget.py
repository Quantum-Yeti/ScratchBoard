from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout

from views.widgets.reference_widget import ReferenceWidget


class ReferencePopup(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: Custom Links")
        self.resize(500, 700)



        # Allow minimize / close independently
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.NonModal)  # Non-blocking

        layout = QVBoxLayout(self)

        # Embed your existing widget inside the dialog
        self.ref_view = ReferenceWidget(model)
        layout.addWidget(self.ref_view)