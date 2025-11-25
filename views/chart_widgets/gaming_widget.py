from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QHBoxLayout, QPushButton, QLabel, QWidget, QVBoxLayout, \
    QDialog, QSizePolicy

from utils.resource_path import resource_path
from views.chart_widgets.chart_dictionaries.gaming_dict import gaming_server_issues

class GamingReference(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply a chart theme if available
        try:
            with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

        self.setWindowTitle("Scratch Board: Gaming Network Reference Chart")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1200, 900)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top icon + title
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        image_label.setPixmap(QPixmap(resource_path("resources/icons/gaming.png")))  # Add your gaming icon
        image_label.setAlignment(Qt.AlignVCenter)

        title_label = QLabel("Gaming Network Reference Chart")
        font = QFont("Segoe UI", 32)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)
        layout.addWidget(icon_title_widget, alignment=Qt.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Metric / Signal",
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
        self.table.setRowCount(len(gaming_server_issues))
        for row, sig in enumerate(gaming_server_issues):
            for col, key in enumerate(["name", "range", "symptoms", "explanation", "steps"]):
                item = QTableWidgetItem(sig[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(sig[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 350)
        self.table.setColumnWidth(4, 300)

        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)