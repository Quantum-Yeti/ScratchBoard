from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView
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
                {"title": "DownDetector: End-User Reported Outages", "url": "https://downdetector.com"},
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

    def on_item_hover(self, item):
        self.list_widget.setCursor(Qt.PointingHandCursor)
    def leaveEvent(self, event):
        self.list_widget.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
