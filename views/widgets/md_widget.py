from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel
from PySide6.QtCore import Qt

from utils.resource_path import resource_path

# Load the QSS theme for the Markdown guide table
with open(resource_path("ui/themes/md_chart_theme.qss"), "r") as f:
    md_chart_theme = f.read()

def get_markdown_guide():
    """
    Returns a list of markdown features with their syntax and rendered HTML representation.

    Each entry in the list is a tuple:
        (Feature Name, Markdown Syntax, Rendered HTML/None)

    The 'Image' feature uses None as rendered HTML, which is handled separately
    by displaying a QPixmap instead.
    """
    # Path to the example image used in the table
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
    """
    Widget that displays a Markdown quick guide in a QTableWidget.

    Features:
        - Three columns: Feature, Markdown Syntax, Rendered Output
        - Custom QSS styling loaded from md_chart_theme
        - Supports images in the Rendered column
        - Non-editable table with word wrap
    """
    def __init__(self):
        """Initializes the MarkdownGuideWidget UI and populates the table."""
        super().__init__()

        # Window settings
        self.setWindowTitle("Scratch Board: Markdown Quick Guide")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setFixedSize(780, 680)

        # Main vertical layout
        layout = QVBoxLayout(self)

        # QTableWidget
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Feature", "Markdown Syntax", "Rendered"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setWordWrap(True)
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 300)
        table.setShowGrid(False)
        table.setStyleSheet(md_chart_theme)

        # Default row height (adjust as needed)
        table.verticalHeader().setDefaultSectionSize(55)

        # Get the Markdown guide data and populate table
        guide = get_markdown_guide()
        table.setRowCount(len(guide)) # allocates rows

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
                # Load QPixmap and scale for the example image
                pixmap = QPixmap(resource_path("resources/icons/image_example.png"))
                rendered_label = QLabel()
                rendered_label.setPixmap(pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                rendered_label.setAlignment(Qt.AlignCenter)
            else:
                # HTML/text rendering
                rendered_label = QLabel()
                rendered_label.setTextFormat(Qt.RichText)
                rendered_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                rendered_label.setOpenExternalLinks(True)
                rendered_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                rendered_label.setText(rendered)
                rendered_label.setMinimumHeight(1)

            table.setCellWidget(row, 2, rendered_label)

            #table.resizeRowToContents(row)

        # Add table to the main layout
        layout.addWidget(table)
