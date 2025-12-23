from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QFont, QPixmap, Qt
from PySide6.QtWidgets import QTableWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QVBoxLayout, QDialog, \
    QWidget, QTableWidgetItem

from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path
from views.info_chart_widgets.info_dictionaries.protocol_dict import internet_protocols


class InternetProtocolsTimeline(QDialog):
    """
    Shows a timeline of major recent internet protocols, their eras, purpose, and notes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        with open(resource_path("ui/themes/charts_theme.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.setWindowTitle("Scratch Board: Recent Internet Protocols")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(1200, 900)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top image and title
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel()
        image_label.setPixmap(QPixmap(resource_path("resources/icons/server_yellow.png")))
        image_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel("Internet Protocols Timeline")
        font = QFont("Segoe UI", 32)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)
        layout.addWidget(icon_title_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Protocol", "Era", "Purpose", "Notes"
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

        # Populate table
        self._populate_table()
        self._resize_table()

    def _populate_table(self):
        self.table.setRowCount(len(internet_protocols))
        for row, proto in enumerate(internet_protocols):
            for col, key in enumerate(["protocol", "era", "purpose", "notes"]):
                item = QTableWidgetItem(proto[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                item.setToolTip(proto[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        self.table.setColumnWidth(0, 250)  # Protocol
        self.table.setColumnWidth(1, 150)  # Era
        self.table.setColumnWidth(2, 300)  # Purpose
        self.table.setColumnWidth(3, 450)  # Notes
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)