from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout

from views.widgets.mac_widget import MacVendorView


class MacVendorPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: MAC Vendor Query")
        self.resize(500, 400)

        # Allow minimize / close independently
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.NonModal)  # Non-blocking

        layout = QVBoxLayout(self)

        # Embed your existing widget inside the dialog
        self.mac_view = MacVendorView()
        layout.addWidget(self.mac_view)
