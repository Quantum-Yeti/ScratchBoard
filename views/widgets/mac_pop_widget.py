from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout

from utils.custom_context_menu import ContextMenuUtility
from views.widgets.mac_widget import MacVendorView


class MacVendorPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scratch Board: MAC Vendor Query")
        self.resize(500, 400)

        # Allow minimizing / close independently
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)  # Non-blocking

        layout = QVBoxLayout(self)

        # Embed your existing widget inside the dialog
        self.mac_view = MacVendorView()
        layout.addWidget(self.mac_view)

        # Override context menu
        self.context_menu_helper = ContextMenuUtility(self.mac_view)
