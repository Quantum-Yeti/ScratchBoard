from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path
from views.chart_widgets.chart_dictionaries.ethernet_dict import ethernet_specs


class EthernetReference(QDialog):
    """
    Displays a reference table of Ethernet cable categories,
    their capabilities, and typical use cases.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply the chart_theme.qss
        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Ethernet Cable Reference Chart")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1100, 900)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top image and title of chart
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignCenter)  # Centers everything horizontally

        # Image
        image_label = QLabel()
        image_label.setPixmap(QPixmap(resource_path("resources/icons/ethernet_purple.png")))
        image_label.setAlignment(Qt.AlignVCenter)

        # Title
        title_label = QLabel("Ethernet Reference Chart")
        font = QFont("Segoe UI", 32)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)  # Prevents stretching

        # Add widgets to layout
        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)

        # Add the container widget to the main layout
        layout.addWidget(icon_title_widget, alignment=Qt.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Category",
            "Max Speed",
            "Max Bandwidth",
            "Max Length",
            "PoE Support",
            "Typical Use Cases"
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

        # Fill table & adjust size
        self._populate_table()
        self._resize_table()

    def _populate_table(self):
        self.table.setRowCount(len(ethernet_specs))

        keys = ["cat", "speed", "bandwidth", "length", "poe", "use"]

        for row, entry in enumerate(ethernet_specs):
            for col, key in enumerate(keys):
                item = QTableWidgetItem(entry[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(entry[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 110)  # Category
        self.table.setColumnWidth(1, 140)  # Speed
        self.table.setColumnWidth(2, 150)  # Bandwidth
        self.table.setColumnWidth(3, 120)  # Length
        self.table.setColumnWidth(4, 140)  # PoE
        self.table.setColumnWidth(5, 300)  # Use cases

        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
