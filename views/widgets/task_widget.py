from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QHBoxLayout, QListWidget, QListWidgetItem
)

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

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_reminder)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

    def add_reminder(self):
        text = self.input_field.text().strip()
        if not text:
            return

        # Create a horizontal layout for each item
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(5)

        # Reminder text
        label = QLabel(text)
        label.setStyleSheet("background-color: #2e2e2e; color: #9ACEEB;")
        item_layout.addWidget(label)

        # Mark done button
        done_button = QPushButton("Done")
        done_button.setMaximumWidth(60)
        done_button.clicked.connect(lambda _, iw=item_widget: self.mark_done(iw))
        item_layout.addWidget(done_button)

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
