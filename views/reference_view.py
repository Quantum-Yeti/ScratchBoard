from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

class ReferenceWidget(QWidget):
    def __init__(self, references=None):
        super().__init__()
        self.setObjectName("ReferenceWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Sample references if none provided
        if references is None:
            references = [
                {"title": "How Modems Work", "url": "https://www.scientificamerican.com/article/how-modems-work/"},
                {"title": "Understanding Routers", "url": "https://ieeexplore.ieee.org/document/xxxxxx"},
                {"title": "Digital Communication Basics", "url": "https://www.sciencedirect.com/science/article/pii/xxxxxx"},
            ]

        for ref in references:
            item = QListWidgetItem(ref["title"])
            item.setData(Qt.UserRole, ref["url"])
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.open_reference)

    def open_reference(self, item):
        url = item.data(Qt.UserRole)
        QDesktopServices.openUrl(QUrl(url))
