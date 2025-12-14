from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt, QSize

from ui.menus.shortcuts_list import shortcut_list
from utils.resource_path import resource_path

class ShortcutGuide(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Scratch Board: Keyboard Shortcuts")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(650, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header with icon + title
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout(icon_title_widget)
        icon_title_layout.setSpacing(10)
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        image_label.setPixmap(
            QPixmap(resource_path("resources/icons/keyboard.png")).scaled(64, 64)
        )
        image_label.setAlignment(Qt.AlignVCenter)

        title_label = QLabel("Keyboard Shortcuts")
        font = QFont("Segoe UI", 24)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        icon_title_layout.addWidget(image_label)
        icon_title_layout.addWidget(title_label)
        layout.addWidget(icon_title_widget, alignment=Qt.AlignCenter)

        # Shortcut Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
            QScrollBar::handle:vertical {
                background: #a8b8c8;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        self._populate_table()
        layout.addWidget(self.table)

        # Close Button
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

    # Populate Table Category Header + Shortcut Rows
    def _populate_table(self):
        total_rows = sum(len(cat["shortcuts"]) + 1 for cat in shortcut_list)
        self.table.setRowCount(total_rows)

        row = 0
        for cat in shortcut_list:

            # Category Header Row
            category_item = QTableWidgetItem(cat["category"])
            category_item.setFlags(Qt.ItemIsEnabled)
            category_item.setTextAlignment(Qt.AlignCenter)
            category_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

            # Span across both columns
            self.table.setItem(row, 0, category_item)
            self.table.setSpan(row, 0, 1, 2)
            row += 1

            # Shortcut Rows
            for sc in cat["shortcuts"]:
                shortcut_item = QTableWidgetItem(sc["shortcut"])
                shortcut_item.setFlags(Qt.ItemIsEnabled)

                action_item = QTableWidgetItem(sc["action"])
                action_item.setFlags(Qt.ItemIsEnabled)

                self.table.setItem(row, 0, shortcut_item)
                self.table.setItem(row, 1, action_item)
                row += 1
