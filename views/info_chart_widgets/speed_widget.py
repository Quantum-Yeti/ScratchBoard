from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt, QSize

from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from views.info_chart_widgets.info_dictionaries.speed_dict import requirements


class InternetSpeedRequirements(QDialog):
    """
    Shows common internet use-cases with recommended and minimum speeds,
    plus latency expectations and notes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply the chart_theme.qss
        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Bandwidth Requirements Chart")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(1100, 900)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top image and title of chart
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centers everything horizontally

        # Image
        image_label = QLabel()
        image_label.setPixmap(QPixmap(resource_path("resources/icons/bandwidth.png")))
        image_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Title
        title_label = QLabel("Bandwidth Requirements Chart")
        font = QFont("Segoe UI", 32)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)  # Prevents stretching

        # Add widgets to layout
        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)

        # Add the container widget to the main layout
        layout.addWidget(icon_title_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Activity / Application",
            "Minimum Speed",
            "Recommended Speed",
            "Latency Requirement",
            "Notes"
        ])
        self.table.setWordWrap(True)
        self.table.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.table.horizontalScrollBar().setStyleSheet(vertical_scrollbar_style)
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

        # fill the table
        self._populate_table()
        self._resize_table()

    def _populate_table(self):
        self.table.setRowCount(len(requirements))
        for row, req in enumerate(requirements):
            for col, key in enumerate(["activity", "min", "rec", "latency", "notes"]):
                item = QTableWidgetItem(req[key])
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                item.setToolTip(req[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 250)  # Activity
        self.table.setColumnWidth(1, 120)  # Min speed
        self.table.setColumnWidth(2, 160)  # Rec speed
        self.table.setColumnWidth(3, 130)  # Latency
        self.table.setColumnWidth(4, 350)  # Notes

        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
