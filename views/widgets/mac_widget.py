from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QTextEdit, QHBoxLayout, \
    QSizePolicy

from ui.themes.mac_widget_style import mac_widget_style
from utils.resource_path import resource_path

from helpers.modules.oui_lookup import OUILookup

class MacVendorView(QWidget):
    """
    A QWidget-based interface for looking up MAC address vendor information.

    Features:
    - Input field for MAC addresses.
    - Query and Clear buttons.
    - Console-style output showing results in a styled QTextEdit.
    """
    def __init__(self):
        """ Initialize the MacVendorView GUI, layouts, and components."""
        super().__init__()

        # Connect to MAC lookup function
        self.oui = OUILookup()

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2,2,0,2)
        layout.setSpacing(6)

        # Console-style output area
        self.console_output = QTextEdit()
        self.console_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.console_output.setPlaceholderText("Console output area.")
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(0)
        self.console_output.setStyleSheet(mac_widget_style)
        layout.addWidget(self.console_output, stretch=1)

        # Horizontal layout for input + buttons
        input_layout = QHBoxLayout()

        # MAC Entry field
        self.input_mac = QLineEdit()
        self.input_mac.setPlaceholderText("Enter MAC (e.g., 00:1A:2B:33:44:55)")
        input_layout.addWidget(self.input_mac, 1)  # input on the left

        # Add stretch so buttons move to the right
        input_layout.addStretch()

        # Query button
        mac_query_btn = QPushButton()
        mac_query_btn.setToolTip("Query")
        mac_query_btn.setIcon(QIcon(resource_path("resources/icons/db_search.png")))
        mac_query_btn.setMaximumSize(75, 30)
        mac_query_btn.setIconSize(QSize(20, 20))
        mac_query_btn.clicked.connect(self.lookup_mac)
        input_layout.addWidget(mac_query_btn)

        # Clear button
        clear_btn = QPushButton()
        clear_btn.setToolTip("Clear")
        clear_btn.setIcon(QIcon(resource_path("resources/icons/cancel_blue.png")))
        clear_btn.setMaximumSize(75, 30)
        clear_btn.setIconSize(QSize(24, 24))
        clear_btn.clicked.connect(self.clear_btn)
        input_layout.addWidget(clear_btn)

        # Add the combined row to the main layout
        layout.addLayout(input_layout)

    def append_console(self, text):
        """
        Append text to the console output with a newline and auto-scroll to the bottom.

        Args:
            text (str): Text to append to the console.
        """
        self.console_output.append(text + "\n")
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def lookup_mac(self):
        """
        Perform a MAC address lookup using the OUILookup module.
        Displays results in the console output area.
        """
        mac = self.input_mac.text().strip()

        # MAC Validation
        if len(mac) < 6:
            QMessageBox.warning(self, "Error", "Enter a valid MAC address.")
            return

        vendor, address, prefix_type = self.oui.lookup(mac)

        # Styled console output + clear console
        self.console_output.clear()
        self.append_console(f"> MAC: {mac}")
        self.append_console(f"> Vendor: {vendor}")
        self.append_console(f"> Country: {address}")
        self.append_console(f"> Type: {prefix_type}")

    def clear_btn(self):
        """
        Clear the MAC input field and console output.
        Warns the user if there is nothing to clear.
        """
        if not self.input_mac.text().strip() and not self.console_output.toPlainText().strip():
            QMessageBox.warning(self, "Error", "Nothing to clear.")
            return

        self.input_mac.clear()
        self.console_output.clear()
