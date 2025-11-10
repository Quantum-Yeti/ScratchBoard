import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox


class MacVendorView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)
        layout.setSpacing(6)

        title = QLabel("MAC Vendor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        layout.addWidget(title)

        self.input_mac = QLineEdit()
        self.input_mac.setPlaceholderText("Enter MAC Address (e.g., 00:00:ff:00:cc:00")
        layout.addWidget(self.input_mac)

        button = QPushButton("Query")
        button.clicked.connect(self.lookup_mac)
        layout.addWidget(button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.result_label)

    def lookup_mac(self):
        mac = self.input_mac.text().strip()

        if not mac:
            QMessageBox.warning(self, "Error", "Enter a valid MAC Address.")
            return

        try:
            response = requests.get(f"https://macvendorlookup.com/api/v2/{mac}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    vendor = data[0]
                    company = vendor.get("company", "Unknown")
                    country = vendor.get("country", "Unknown")
                    type = vendor.get("type", "Unknown")
                    self.result_label.setText(f"{company} ({country})\n{type}")
                else:
                    QMessageBox.warning(self, "Invalid MAC", "Vendor not found..")
            else:
                self.result_label.setText("Vendor not found")
        except Exception as e:
            QMessageBox.critical(self, "Network Error", str(e))
