from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QDialog, QStyle, \
    QApplication
from helpers.modules.modem_log_parser import ModemLogParser
from PySide6.QtCore import Qt, QSize

from utils.resource_path import resource_path


class ModemLogParserView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)  # important to pass parent
        self.setWindowTitle("Scratch Board: Modem Log Parser")
        self.setWindowModality(Qt.ApplicationModal)  # makes it modal

        self.parser = ModemLogParser()

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

        # Aligns parse + clear buttons
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

        self.resize(900, 700)
        self.setMinimumSize(QSize(900, 700))
        self.setMaximumSize(QSize(1200, 900))

        self.setGeometry(
            QStyle.alignedRect (
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                QApplication.primaryScreen().availableGeometry()
            )
        )

    def parse_logs(self):
        raw = self.input.toPlainText()
        if not raw.strip():
            self.output.setPlainText("No logs provided.")
            return

        events = self.parser.parse(raw)
        summary = self.parser.summarize(events)

        # Build readable summary
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
        self.input.clear()
        self.output.clear()
        self.summary_label.clear()