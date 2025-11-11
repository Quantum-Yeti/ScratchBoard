from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit
from fontTools.merge import layout

from helpers.oui_lookup import OUILookup


class MacVendorView(QWidget):
    def __init__(self):
        super().__init__()

        self.oui = OUILookup()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        layout.addWidget(title)

        # MAC Entry field
        self.input_mac = QLineEdit()
        self.input_mac.setPlaceholderText("Enter MAC (ex: 00:1A:2B:33:44:55)")
        layout.addWidget(self.input_mac)

        # Console-style output area
        self.console_output = QTextEdit()
        self.console_output.setPlaceholderText("Console Output...")
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(100)
        self.console_output.setStyleSheet("""
                    background-color: #111;
                    color: #00FF7F;
                    font-family: Consolas, monospace;
                    border: 1px solid #444;
                    padding: 6px;
                """)
        layout.addWidget(self.console_output)

        # Query button
        button = QPushButton("Lookup")
        button.clicked.connect(self.lookup_mac)
        layout.addWidget(button)

    def append_console(self, text):
        self.console_output.append(text)
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def lookup_mac(self):
        mac = self.input_mac.text().strip()

        if len(mac) < 6:
            QMessageBox.warning(self, "Error", "Enter a valid MAC address.")
            return

        vendor, address, prefix_type = self.oui.lookup(mac)

        # Styled console output
        self.console_output.clear()
        self.append_console(f"> MAC: {mac}")
        self.append_console(f"> Vendor: {vendor}")
        self.append_console(f"> Country: {address}")
        self.append_console(f"> Type: {prefix_type}")
