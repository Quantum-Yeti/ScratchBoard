from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QDialog

from views.widgets.batch_widget import BatchWidget


class BatchPopup(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scratch Board: Batch Manager")
        self.resize(580, 480)

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)

        layout = QVBoxLayout(self)
        layout.addWidget(BatchWidget(model))