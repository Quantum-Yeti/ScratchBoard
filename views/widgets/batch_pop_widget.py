from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QDialog

from utils.resource_path import resource_path
from views.widgets.batch_widget import BatchWidget


class BatchPopup(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scratch Board: Batch Manager")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut_main.ico")))
        self.setFixedSize(580, 480)

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)

        layout = QVBoxLayout(self)
        layout.addWidget(BatchWidget(model))