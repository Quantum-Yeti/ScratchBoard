from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QSizePolicy, QLabel, QWidget
)
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path
from views.info_widgets.info_dictionaries.wifi_dict import standards


class WifiStandardsReference(QDialog):
    """
    Reference chart for Wi-Fi standards including speeds, frequencies,
    features, and real-world performance expectations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply the chart_theme.qss
        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Wi-Fi Standards Reference Chart")
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
        image_label.setPixmap(QPixmap(resource_path("resources/icons/wifi_channel.png")))
        image_label.setAlignment(Qt.AlignVCenter)

        # Title
        title_label = QLabel("WiFi Standards Reference Chart")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Standard",
            "Max Speed",
            "Bands",
            "Channel Width",
            "MIMO / Features",
            "Real-World Speed",
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
        self.table.setRowCount(len(standards))
        for row, wifi in enumerate(standards):
            for col, key in enumerate(["std", "speed", "bands", "width", "features", "real", "notes"]):
                item = QTableWidgetItem(wifi[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(wifi[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 130)  # Standard
        self.table.setColumnWidth(1, 120)  # Max speed
        self.table.setColumnWidth(2, 110)  # Bands
        self.table.setColumnWidth(3, 130)  # Channel width
        self.table.setColumnWidth(4, 220)  # Features
        self.table.setColumnWidth(5, 150)  # Real speed
        self.table.setColumnWidth(6, 260)  # Notes

        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
