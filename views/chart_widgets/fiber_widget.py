from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QSizePolicy, QLabel, QWidget
)
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path
from views.chart_widgets.chart_dictionaries.fiber_dict import signals


class FiberReferenceDialog(QDialog):
    """Fiber Modem / ONT Reference Chart Dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply the chart_theme.qss
        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Fiber Modem Reference Chart")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1200, 900)

        # Main layout
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
        image_label.setPixmap(QPixmap(resource_path("resources/icons/waves.png")))
        image_label.setAlignment(Qt.AlignVCenter)

        # Title
        title_label = QLabel("Fiber Signal Reference Chart")
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Signal / Metric",
            "Normal Range",
            "Symptoms / Common Issues",
            "Explanation",
            "Troubleshooting Steps"
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

        # Populate table
        self._populate_table()
        self._resize_table()

    def _populate_table(self):
        self.table.setRowCount(len(signals))
        for row, sig in enumerate(signals):
            for col, key in enumerate(["name", "range", "symptoms", "explanation", "steps"]):
                item = QTableWidgetItem(sig[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(sig[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 300)
        self.table.setColumnWidth(4, 250)
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
