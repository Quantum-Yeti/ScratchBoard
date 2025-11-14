from PySide6 import QtCore
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, Qt, QAction, QIcon
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QListWidget, QHBoxLayout, QLineEdit, QPushButton, QWidget, \
    QMenu, QMessageBox, QLabel
from utils.resource_path import resource_path


class ReferenceWidget(QWidget):
    def __init__(self, model):
        super().__init__()
        # Initialize model
        self.model = model

        # Vertical box layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)
        layout.setSpacing(6)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.list_widget)

        # Input for adding new references
        input_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title...")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL (https://...)")

        self.add_button = QPushButton("")
        self.add_button.setIcon(QIcon(resource_path("resources/icons/add.png")))
        self.add_button.clicked.connect(self.add_reference)

        input_layout.addWidget(self.title_input)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        # Initialize the loading of references
        self.load_references()
        # Allow reference to open on click
        self.list_widget.itemClicked.connect(self.open_reference)

    def load_references(self):
        self.list_widget.clear()
        for ref in self.model.get_references():
            item = QListWidgetItem(f"> {ref["title"]}")
            item.setData(Qt.UserRole, ref["url"])
            item.setData(Qt.UserRole + 1, ref["id"])  # store the database ID for deletion

            # Adds extra vertical spacing
            item.setSizeHint(item.sizeHint() + QtCore.QSize(0, 3))

            self.list_widget.addItem(item)

    def add_reference(self):
        title = self.title_input.text().strip()
        url = self.url_input.text().strip()
        if not title or not url:
            return
        self.model.add_reference(title, url)
        self.load_references()
        self.title_input.clear()
        self.url_input.clear()

    def open_reference(self, item):
        QDesktopServices.openUrl(QUrl(item.data(Qt.UserRole)))

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu()
            delete_action = QAction("Delete", self)
            # Pass the reference ID stored in Qt.UserRole (or store it when loading)
            delete_action.triggered.connect(lambda: self.delete_reference(item))
            menu.addAction(delete_action)
            menu.exec(self.list_widget.mapToGlobal(pos))

    def delete_reference(self, item):
        ref_id = item.data(Qt.UserRole + 1)  # store the ref_id separately when loading
        reply = QMessageBox.question(
            self,
            "Delete Reference",
            f"Delete '{item.text()}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.model.delete_reference(ref_id)
            self.load_references()
