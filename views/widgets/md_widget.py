from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel
from PySide6.QtCore import Qt

from utils.resource_path import resource_path


def get_markdown_guide():
    """Returns a list of markdown features with their syntax and rendered HTML."""
    return [
        ("Bold", "**bold**", "<b>bold</b>"),
        ("Italic", "*italic*", "<i>italic</i>"),
        ("Header H1", "# H1", "<h1>H1</h1>"),
        ("Header H2", "## H2", "<h2>H2</h2>"),
        ("Header H3", "### H3", "<h3>H3</h3>"),
        ("Bulleted list", "- Item", "• Item"),
        ("Numbered list", "1. Item", "1. Item"),
        ("Link", "[Example Website Name](https://example.com)", '<a href="https://example.com">Example Website Name</a>'),
        ("Image", "![Title of image](path/to/image/here)", '<img src="resources/icons/landscape.png">'),
        ("Inline code", "Inline code", '<code>Inline code</code>'),
        ("Code block", "```python\nprint('Hello World')\n```", '<pre>print("Hello World")</pre>')
    ]

class MarkdownGuideWidget(QWidget):
    def __init__(self):
        """Builds the Markdown Guide widget."""
        super().__init__()
        self.setWindowTitle("Scratch Board: Markdown Quick Guide")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(780, 475)

        layout = QVBoxLayout(self)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Feature", "Markdown Syntax", "Rendered"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setWordWrap(True)
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 300)

        guide = get_markdown_guide()
        table.setRowCount(len(guide))

        for row, (feature, syntax, rendered) in enumerate(guide):
            # Feature column
            feature_label = QLabel(feature)
            feature_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setCellWidget(row, 0, feature_label)

            # Markdown syntax column
            syntax_label = QLabel(syntax)
            syntax_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setCellWidget(row, 1, syntax_label)

            # Rendered column (HTML)
            rendered_label = QLabel()
            rendered_label.setTextFormat(Qt.RichText)
            rendered_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            rendered_label.setOpenExternalLinks(True)
            rendered_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            rendered_label.setText(rendered)
            rendered_label.setMinimumHeight(1)
            table.setCellWidget(row, 2, rendered_label)

            table.resizeRowToContents(row)

        layout.addWidget(table)
