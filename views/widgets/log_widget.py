from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QDialog, QStyle, \
    QApplication
from helpers.modules.modem_log_parser import ModemLogParser
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path

class ModemLogParserView(QDialog):
    """
    A modal dialog window for parsing and displaying DOCSIS modem event logs.

    Features:
        - Input area for modem logs
        - Parse button to analyze logs
        - Clear button to reset the input and output
        - Summary display of events and severity
        - Detailed log output with explanations
    """
    def __init__(self, parent=None):
        """
        Initialize the ModemLogParserView class.
        """
        super().__init__(parent)  # important to pass parent
        self.setWindowTitle("Scratch Board: Modem Log Parser")
        self.setWindowModality(Qt.ApplicationModal)  # makes it modal

        # Initialize the log parser
        self.parser = ModemLogParser()

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Input field
        self.input = QTextEdit()
        self.input.setPlaceholderText("Paste modem event logs here...")
        self.input.setMinimumHeight(200)
        layout.addWidget(self.input)

        # Parse button
        parse_btn = QPushButton("Parse Logs")
        parse_btn.setIcon(QIcon(resource_path("resources/icons/query.png")))
        parse_btn.clicked.connect(self.parse_logs)

        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.setIcon(QIcon(resource_path("resources/icons/clear.png")))
        clear_btn.clicked.connect(self.clear_logs)

        # Button row - aligns parse + clear buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(parse_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Output summary
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignLeft)
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Detailed output
        self.output = QTextEdit()
        self.output.setPlaceholderText("Log output...")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(350)
        layout.addWidget(self.output)

        # Set dialog size constraints
        self.resize(900, 700)
        self.setMinimumSize(QSize(900, 700))
        self.setMaximumSize(QSize(1200, 900))

        # Center the dialog on screen
        self.setGeometry(
            QStyle.alignedRect (
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                QApplication.primaryScreen().availableGeometry()
            )
        )

    def parse_logs(self):
        """
        Parse the modem event logs within the input field.

        Process the logs through ModemLogParser, display a summarized event count, severity overview, and
        show the detailed event information.
        """
        raw = self.input.toPlainText()
        if not raw.strip():
            self.output.setPlainText("No logs provided.")
            return

        # Parse and summarize
        events = self.parser.parse(raw)
        summary = self.parser.summarize(events)

        # Build readable summary text
        summary_txt = ""
        for cat, data in summary.items():
            summary_txt += f"• {cat}: {data['count']} events (Severity: {data['severity']})\n"
        self.summary_label.setText(summary_txt)

        # Detailed event dump
        lines = []
        for ev in events:
            lines.append(
                f"[{ev.timestamp}] ({ev.category}/{ev.severity})\n"
                f"{ev.message}\n"
                f"→ {ev.explanation}\n"
            )
            if ev.steps:
                lines.append("Steps to troubleshoot:")
                for step in ev.steps:
                    lines.append(f"  • {step}")
            lines.append("-------------------------")

        self.output.setPlainText("\n".join(lines))

    def clear_logs(self):
        """
        Clear all input, summary, and output fields in the dialog.
        """
        self.input.clear()
        self.output.clear()
        self.summary_label.clear()