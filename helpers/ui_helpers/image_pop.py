from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class ImagePopup:
    """
    Utility class to display an image in a popup dialog with optional scaling and scroll support.

    Features:
        - Shows any image in a resizable popup dialog.
        - Automatically scales the image to fit the dialog's viewport, preserving aspect ratio.
        - Supports window resizing: image resizes dynamically.
        - Scrollable for large images.

    Methods:
        show(parent, path, margin_ratio=0.98)

    Methods:
        show(parent, path, margin_ratio=0.98):
            Display the image in a popup dialog.

            Args:
                :param parent (QWidget): The parent widget for the popup dialog.
                :param path (str): Path to the image file to display.
                :param margin_ratio (float, optional): Fraction of the viewport size to use for scaling the image.
                    Default is 0.98 (i.e., 98% of the available scroll area).

            Behavior:
                - Loads the image from the given path.
                - Scales the image to fit within the dialog's scrollable viewport,
                  maintaining the original aspect ratio.
                - Updates the image size dynamically if the dialog is resized.
                - Displays the image in a modal dialog, blocking interaction with the parent
                  until the dialog is closed.
    """
    @staticmethod
    def show(parent, path, margin_ratio=0.98):
        dlg = QDialog(parent)
        dlg.setWindowTitle("Scratch Board: Image Viewer")
        dlg.resize(900, 700)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll)

        lbl = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load original pixmap once
        pix = QPixmap(path)
        lbl.original_pixmap = pix  # store it

        scroll.setWidget(lbl)

        # Function to scale pixmap whenever window changes
        def resize_image():
            viewport_size = scroll.viewport().size()
            max_width = int(viewport_size.width() * margin_ratio)
            max_height = int(viewport_size.height() * margin_ratio)
            scaled = lbl.original_pixmap.scaled(
                max_width,
                max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            lbl.setPixmap(scaled)

        # Connect resizing
        dlg.resizeEvent = lambda event: (resize_image(), QDialog.resizeEvent(dlg, event))
        dlg.show()
        resize_image()  # initial scale

        dlg.exec()
