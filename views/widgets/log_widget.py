from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QDialog, QApplication, QFrame
from helpers.modules.modem_log_parser import ModemLogParser
from PySide6.QtCore import Qt, QSize

from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path


def _make_divider():
    divider = QFrame()
    divider.setFrameShape(QFrame.Shape.HLine)
    divider.setFrameShadow(QFrame.Shadow.Sunken)
    divider.setStyleSheet("color: #aaa;")
    return divider


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

        # Input label
        input_label = QLabel("Modem Log")
        input_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(input_label)

        # Input field
        self.input = QTextEdit()
        self.input.setPlaceholderText("Paste modem event logs here...")
        self.input.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.input.setMinimumHeight(200)
        layout.addWidget(self.input)

        # Button row - aligns parse + clear buttons
        button_row = QHBoxLayout()
        button_row.addStretch() # Left stretch

        parse_btn = QPushButton("Parse Logs")
        parse_btn.setIcon(QIcon(resource_path("resources/icons/query.png")))
        parse_btn.clicked.connect(self.parse_logs)
        button_row.addWidget(parse_btn)

        clear_btn = QPushButton("Clear Logs")
        clear_btn.setIcon(QIcon(resource_path("resources/icons/clear.png")))
        clear_btn.clicked.connect(self.clear_logs)
        button_row.addWidget(clear_btn)

        button_row.addStretch() # Right stretch

        layout.addLayout(button_row)

        # Output label
        self.summary_title = QLabel("Summary:")
        self.summary_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.summary_title)

        # Output summary
        self.summary_label = QLabel("Waiting on input...")
        self.summary_label.setAlignment(Qt.AlignLeft)
        self.summary_label.setStyleSheet("color: #00A3E0;")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Output label
        self.output_label = QLabel("Detailed Log Analysis")
        self.output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.output_label)

        # Detailed output
        self.output = QTextEdit()
        self.output.setPlaceholderText("Log output...")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(350)
        self.output.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        layout.addWidget(self.output)

        # Set dialog size constraints
        self.resize(1200, 900)
        self.setMinimumSize(QSize(900, 700))
        self.setMaximumSize(QSize(1400, 1200))

        self.center_on_screen(parent)

        # Center the dialog on screen
        #self.setGeometry(
            #QStyle.alignedRect (
                #Qt.LeftToRight,
                #Qt.AlignCenter,
                #self.size(),
                #QApplication.primaryScreen().availableGeometry()
            #)
        #)

    def center_on_screen(self, parent=None):
        if parent:
            parent_geometry = parent.frameGeometry()
            parent_center = parent_geometry.center()
            self.move(parent_center - self.rect().center())
        else:
            cursor_position = QCursor.pos()
            screen = QApplication.screenAt(cursor_position)
            if not screen:
                screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            self.move(screen_geometry.center() - self.rect().center())


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

