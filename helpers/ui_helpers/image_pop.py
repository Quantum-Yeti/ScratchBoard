from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class ImagePopup:
    @staticmethod
    def show(parent, path, margin_ratio=0.98):
        """
        Show an image in a popup dialog with scroll support.

        Args:
            parent: parent QWidget
            path: image file path
            margin_ratio: ratio of scroll area to use for image scaling
        """
        dlg = QDialog(parent)
        dlg.setWindowTitle("Image Viewer")
        dlg.resize(900, 700)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll)

        lbl = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pix = QPixmap(path)

        dlg.show()  # ensures sizes are calculated
        viewport_size = scroll.viewport().size()

        max_width = int(viewport_size.width() * margin_ratio)
        max_height = int(viewport_size.height() * margin_ratio)

        pix = pix.scaled(
            max_width,
            max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        lbl.setPixmap(pix)
        scroll.setWidget(lbl)

        dlg.exec()
