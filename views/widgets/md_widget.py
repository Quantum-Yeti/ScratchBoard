from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel
from PySide6.QtCore import Qt

from utils.resource_path import resource_path

with open(resource_path("ui/themes/md_chart_theme.qss"), "r") as f:
    md_chart_theme = f.read()

def get_markdown_guide():
    """Returns a list of markdown features with their syntax and rendered HTML."""
    image_path = resource_path("resources/icons/image.png")
    rendered_html = f'<img src="file:///{image_path}">'
    return [
        ("Bold", "**bold**", "<b>bold</b>"),
        ("Italic", "*italic*", "<i>italic</i>"),
        ("Header H1", "# H1", "<h1>H1</h1>"),
        ("Header H2", "## H2", "<h2>H2</h2>"),
        ("Header H3", "### H3", "<h3>H3</h3>"),
        ("Bulleted list", "- Item", "• Item"),
        ("Numbered list", "1. Item", "1. Item"),
        ("Link", "[Example Website Name](https://example.com)", '<a href="https://example.com">Example Website Name</a>'),
        ("Image", "![Title of image](path/to/image/here)", None),
        ("Inline code", "Inline code", '<code>Inline code</code>'),
        ("Code block", "```python\nprint('Hello World')\n```", '<pre>print("Hello World")</pre>')
    ]

class MarkdownGuideWidget(QWidget):
    def __init__(self):
        """Builds the Markdown Guide widget."""
        super().__init__()
        self.setWindowTitle("Scratch Board: Markdown Quick Guide")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(780, 680)

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
        table.setShowGrid(False)
        table.setStyleSheet(md_chart_theme)

        table.verticalHeader().setDefaultSectionSize(55)

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
            if rendered is None and feature == "Image":
                # Use QPixmap for image
                pixmap = QPixmap(resource_path("resources/icons/image_example.png"))
                rendered_label = QLabel()
                rendered_label.setPixmap(pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                rendered_label.setAlignment(Qt.AlignCenter)
            else:
                rendered_label = QLabel()
                rendered_label.setTextFormat(Qt.RichText)
                rendered_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                rendered_label.setOpenExternalLinks(True)
                rendered_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                rendered_label.setText(rendered)
                rendered_label.setMinimumHeight(1)

            table.setCellWidget(row, 2, rendered_label)

            #table.resizeRowToContents(row)

        layout.addWidget(table)
