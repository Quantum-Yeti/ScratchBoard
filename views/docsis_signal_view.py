from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path


class SignalReference(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DOCSIS Signal Reference")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(1000, 700)  # initial size

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Signal",
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
        close_btn.setIconSize(QSize(32, 32))
        close_btn.clicked.connect(self.close)

        # Close button wrapped horizontal layout for alignment
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  # left space
        btn_layout.addWidget(close_btn)  # button
        btn_layout.addStretch()  # right space for centering

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(btn_layout)

        # Populate table
        self._populate_table()

        # Resize columns and rows for readability
        self._resize_table()

    def _populate_table(self):
        signals = [
            {
                "name": "Downstream Power (dBmV)",
                "range": "-8 to +10",
                "symptoms": "Too low: intermittent downstream lock\nToo high: distortion, retrains",
                "explanation": "Represents the power at the modem for downstream channels. Out-of-range values indicate coax, splitter, or amplifier issues.",
                "steps": "Check coax connections, splitters, inspect taps or amplifiers."
            },
            {
                "name": "Downstream SNR (dB)",
                "range": ">= 35",
                "symptoms": "Low SNR leads to sync loss or packet errors",
                "explanation": "Signal-to-noise ratio measures quality of downstream signal. Low SNR usually indicates noise on the line or weak signal.",
                "steps": "Check connectors, avoid long coax runs, replace damaged cables, check network noise sources."
            },
            {
                "name": "Upstream Power (dBmV)",
                "range": "+35 to +50",
                "symptoms": "Too low: cannot reach CMTS\nToo high: possible line faults or amplifier issues",
                "explanation": "Power transmitted from modem to CMTS. Out-of-range can affect connectivity.",
                "steps": "Inspect splitter, check line condition, adjust amplifier if available."
            },
            {
                "name": "Correctable Codewords",
                "range": "Low to moderate",
                "symptoms": "High numbers indicate noisy channel",
                "explanation": "Errors that can be corrected by FEC. Too many means signal noise.",
                "steps": "Inspect coax and connectors, reduce interference, check splitters, monitor trends."
            },
            {
                "name": "Uncorrectable Codewords",
                "range": "Very low",
                "symptoms": "High numbers cause packet loss and service degradation",
                "explanation": "Errors that FEC cannot fix. Indicates serious line issues.",
                "steps": "Replace damaged cables and check connectors."
            },
            {
                "name": "T3 Timeout",
                "range": "N/A",
                "symptoms": "Upstream lost intermittently",
                "explanation": "Modem is not hearing CMTS for upstream. Usually noise or line problem.",
                "steps": "Check coax, splitters, noise sources, or plant issues."
            },
            {
                "name": "T4 Timeout",
                "range": "N/A",
                "symptoms": "Modem loses upstream completely",
                "explanation": "Modem fails to range upstream. Often service outage or severe noise.",
                "steps": "Check upstream connectivity, and inspect coax."
            },
            {
                "name": "DHCP / IP Issues",
                "range": "Modem obtains IP",
                "symptoms": "Modem cannot get IP, no internet",
                "explanation": "Indicates provisioning or upstream communication problem.",
                "steps": "Restart modem, check cabling, verify CMTS reachable."
            },
        ]

        self.table.setRowCount(len(signals))
        for row, sig in enumerate(signals):
            for col, key in enumerate(["name", "range", "symptoms", "explanation", "steps"]):
                item = QTableWidgetItem(sig[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip(sig[key])
                self.table.setItem(row, col, item)

    def _resize_table(self):
        # Set initial column widths (helps with wrapping)
        self.table.setColumnWidth(0, 180)  # Signal
        self.table.setColumnWidth(1, 100)  # Range
        self.table.setColumnWidth(2, 200)  # Symptoms
        self.table.setColumnWidth(3, 300)  # Explanation
        self.table.setColumnWidth(4, 250)  # Steps

        # Resize rows to fit wrapped text
        self.table.resizeRowsToContents()

        # Stretch last column to use remaining space
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
