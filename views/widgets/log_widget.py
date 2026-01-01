from PySide6.QtGui import QIcon, QCursor, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QDialog, QApplication, QFrame, \
    QSplitter, QSizePolicy, QMenu
from helpers.parsers.log_parser_helper import ModemLogParser
from PySide6.QtCore import Qt, QSize

from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.custom_context_menu import ContextMenuUtility
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
        """Initialize the ModemLogParserView class."""
        super().__init__(parent)  # important to pass parent
        self.setWindowTitle("Scratch Board: Modem Log Parser")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # makes it modal

        # Initialize the log parser
        self.parser = ModemLogParser()

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Header row (label on left, buttons on right)
        header_row = QHBoxLayout()

        # Title icon
        pixmap = QPixmap(resource_path("resources/icons/polyline.png"))
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(26, 26)
        icon_label.setScaledContents(True)

        # Title label
        title_label = QLabel("Modem Log Parser")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")

        header_row.addWidget(icon_label)
        header_row.addWidget(title_label)

        header_row.addStretch()  # push buttons to the right

        # Parse button
        parse_btn = QPushButton("Parse Logs")
        parse_btn.setIcon(QIcon(resource_path("resources/icons/query.png")))
        parse_btn.setToolTip("Parse Logs")
        parse_btn.clicked.connect(self.parse_logs)
        header_row.addWidget(parse_btn)

        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.setIcon(QIcon(resource_path("resources/icons/clear.png")))
        clear_btn.setToolTip("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        header_row.addWidget(clear_btn)

        # Add the row to the main layout
        layout.addLayout(header_row)

        # Summary label
        self.summary_title = QLabel("Summary:")
        self.summary_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.summary_title)

        # Summary output
        self.summary_label = QLabel("Copy and paste the modem log from your analytics tool to get results.")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.summary_label.setStyleSheet("color: #00A3E0;")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Override context menu for summary
        self.context_menu_helper = ContextMenuUtility(self.summary_label)

        divider = _make_divider()
        layout.addWidget(divider)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Input field
        self.input_title = QLabel("Log Input:")
        self.input = QTextEdit()
        self.input.setPlaceholderText("Paste the modem log here.")
        self.input.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Override context menu for input
        self.context_menu_helper = ContextMenuUtility(self.input)

        # Output field
        self.output_title = QLabel("Log Output:")
        self.output = QTextEdit()
        self.output.setPlaceholderText("Waiting for log to parse.")
        self.output.setReadOnly(True)
        self.output.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        self.output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Override context menu for output
        self.context_menu_helper = ContextMenuUtility(self.output)

        # Add to splitter
        splitter.addWidget(self.input)
        splitter.addWidget(self.output)

        # Sizing behavior
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([500, 700])

        # Add splitter to existing layout
        layout.addWidget(splitter)

        # Set dialog size constraints
        self.resize(1200, 900)
        self.setMinimumSize(QSize(900, 700))
        self.setMaximumSize(QSize(1400, 1200))

        self.center_on_screen(parent)

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
        """Clear all input, summary, and output fields in the dialog."""
        self.input.clear()
        self.output.clear()
        self.summary_label.clear()

