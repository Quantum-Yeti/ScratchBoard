from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox
)

from utils.resource_path import resource_path


class TaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("QuickReminderWidget")
        self.setStyleSheet("""
            QListWidget {
                background: #2E2E2E;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
                color: #9ACEEB;
                font-family: JetBrains Mono, Consolas, monospace;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Reminder list
        self.reminder_list = QListWidget()
        layout.addWidget(self.reminder_list)

        # Input + Add button
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter a reminder...")
        input_layout.addWidget(self.input_field)

        self.add_button = QPushButton()
        self.add_button.setToolTip("Add Task")
        self.add_button.setIcon(QIcon(resource_path("resources/icons/add.png")))
        self.add_button.clicked.connect(self.add_reminder)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

    def add_reminder(self):
        text = self.input_field.text().strip()
        if not text:
            return

        # Create a horizontal layout for each item
        item_widget = QWidget()
        item_widget.setStyleSheet("background-color: transparent;")
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(5)

        # Reminder text
        label = QLabel(text)
        label.setStyleSheet("background-color: transparent; color: #9ACEEB;")
        item_layout.addWidget(label)

        # Mark done button
        done_check = QCheckBox("Done")
        done_check.setStyleSheet("background-color: transparent;")
        done_check.setMaximumWidth(60)
        done_check.clicked.connect(lambda _, iw=item_widget: self.mark_done(iw))
        item_layout.addWidget(done_check)

        item_widget.setLayout(item_layout)

        # Add to QListWidget
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        self.reminder_list.addItem(list_item)
        self.reminder_list.setItemWidget(list_item, item_widget)

        self.input_field.clear()

    def mark_done(self, item_widget):
        # Remove item from the list
        for i in range(self.reminder_list.count()):
            list_item = self.reminder_list.item(i)
            if self.reminder_list.itemWidget(list_item) == item_widget:
                self.reminder_list.takeItem(i)
                break
