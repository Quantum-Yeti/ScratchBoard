from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtWidgets import QTableWidgetItem, QPushButton, QHBoxLayout, QTableWidget, QSizePolicy, QLabel, QWidget, \
    QVBoxLayout, QDialog

from utils.resource_path import resource_path
from views.info_widgets.info_dictionaries.storage_dict import storage


class DiskStorageChart(QDialog):
    """
    Shows common storage units and their equivalences with notes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply the chart theme
        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Disk Storage Info Chart")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(900, 700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top image and title
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignCenter)

        # Image
        image_label = QLabel()
        image_label.setPixmap(QPixmap(resource_path("resources/icons/storage.png")))
        image_label.setAlignment(Qt.AlignVCenter)

        # Title
        title_label = QLabel("Disk Storage Info Chart")
        font = QFont("Segoe UI", 28)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)
        layout.addWidget(icon_title_widget, alignment=Qt.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Unit",
            "Equivalent",
            "Notes"
        ])
        self.table.setWordWrap(True)
        layout.addWidget(self.table)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setIcon(QIcon(resource_path("resources/icons/close_white.png")))
        close_btn.setFixedHeight(36)
        close_btn.setIconSize(QSize(24, 24))
        close_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Fill table
        self._populate_table()
        self._resize_table()

    def _populate_table(self):
        self.table.setRowCount(len(storage))
        for row, req in enumerate(storage):
            for col, key in enumerate(["unit", "equivalent", "notes"]):
                item = QTableWidgetItem(req[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(req[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 150)  # Unit
        self.table.setColumnWidth(1, 200)  # Equivalent
        self.table.setColumnWidth(2, 450)  # Notes
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)