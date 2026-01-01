from PySide6 import QtCore
from PySide6.QtCore import QUrl, QSize
from PySide6.QtGui import QDesktopServices, Qt, QAction, QIcon
from PySide6.QtWidgets import QListWidgetItem, QVBoxLayout, QListWidget, QHBoxLayout, QLineEdit, QPushButton, QWidget, \
    QMenu, QMessageBox, QSizePolicy

from ui.themes.menu_theme import menu_style
from ui.themes.reference_list_style import ref_list_style
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.custom_context_menu import ContextMenuUtility
from utils.resource_path import resource_path


def open_reference(item):
    QDesktopServices.openUrl(QUrl(item.data(Qt.ItemDataRole.UserRole)))


class ReferenceWidget(QWidget):
    def __init__(self, model):
        super().__init__()
        # Initialize model
        self.model = model

        # Vertical box layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        layout.setSpacing(6)

        self.list_widget = QListWidget()
        self.list_widget.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_widget.setStyleSheet(ref_list_style)
        self.list_widget.setViewportMargins(0, 0, 0, 0)
        self.list_widget.viewport().setAutoFillBackground(False)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.list_widget)

        # Input for adding new references
        input_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setToolTip("Enter a title for your link")
        self.title_input.setPlaceholderText("Title...")

        # Override context menu for title
        self.custom_context_menu = ContextMenuUtility(self.title_input)

        self.url_input = QLineEdit()
        self.url_input.setToolTip("Enter a URL for your link")
        self.url_input.setPlaceholderText("URL (https://...)")

        # Override context menus for url
        self.custom_context_menu = ContextMenuUtility(self.url_input)

        self.add_button = QPushButton()
        self.add_button.setToolTip("Add")
        self.add_button.setIcon(QIcon(resource_path("resources/icons/add_circle.png")))
        self.add_button.setIconSize(QSize(18, 18))
        self.add_button.clicked.connect(self.add_reference)

        input_layout.addWidget(self.title_input)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        # Initialize the loading of references
        self.refresh_references()
        self.load_references()
        # Allow reference to open on click
        self.list_widget.itemClicked.connect(open_reference)

    def load_references(self):
        self.list_widget.clear()
        references = self.model.get_references()

        if not references:
            # Add a dummy, disabled item as placeholder
            placeholder_item = QListWidgetItem("Add a custom link for quick access.\nRight-click to delete a link.")
            placeholder_item.setFlags(Qt.ItemFlag.NoItemFlags)  # makes it unselectable
            placeholder_item.setForeground(QtCore.Qt.gray)
            self.list_widget.addItem(placeholder_item)
            return

        for ref in references:
            item = QListWidgetItem(f"> {ref['title']}")
            item.setData(Qt.ItemDataRole.UserRole, ref["url"])
            item.setData(Qt.ItemDataRole.UserRole + 1, ref["id"])  # store the database ID for deletion

            # Adds extra vertical spacing
            item.setSizeHint(item.sizeHint() + QtCore.QSize(0, 3))

            self.list_widget.addItem(item)

    def add_reference(self):
        title = self.title_input.text().strip()
        url = self.url_input.text().strip()

        if not title or not url:
            error = QMessageBox(self)
            error.setIcon(QMessageBox.Icon.Warning)
            error.setWindowTitle("Error")
            error.setText("Title and URL are required.")
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.exec()
            return

        self.model.add_reference(title, url)
        self.load_references()
        self.title_input.clear()
        self.url_input.clear()

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu()
            menu.setStyleSheet(menu_style)
            delete_action = QAction("Delete", self)
            delete_action.setToolTip("Delete")
            delete_action.setIcon(QIcon(resource_path("resources/icons/delete.png")))

            delete_action.triggered.connect(lambda: self.delete_reference(item))
            menu.addAction(delete_action)
            menu.exec(self.list_widget.mapToGlobal(pos))

    def delete_reference(self, item):
        ref_id = item.data(Qt.ItemDataRole.UserRole + 1)  # store the ref_id separately when loading
        reply = QMessageBox.question(
            self,
            "Delete Reference",
            f"Delete '{item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete_reference(ref_id)
            self.load_references()

    def refresh_references(self):
        self.list_widget.blockSignals(True)
        self.load_references()
        self.list_widget.blockSignals(False)

