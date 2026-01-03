import json
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel

from utils.resource_path import resource_path


def update_db_stats(model):
    db_dialog = QDialog()
    db_dialog.setWindowTitle("Scratch Board: Database Stats")
    db_dialog.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
    db_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    db_dialog.setMinimumSize(400, 300)
    db_dialog.setStyleSheet("""
        QDialog {
            background-color: #1E1E1E;
        }
        QLabel {
            font-weight: bold;
            background-color: #1E1E1E;
        }
    """)

    db_layout = QVBoxLayout(db_dialog)

    # Notes / categories / tags
    num_notes = len(model.get_notes())
    num_categories = len(model.get_all_categories())
    tags_list = []
    for note in model.get_notes():
        t = note["tags"]
        if t:
            try:
                t = json.loads(t)
            except:
                t = [t]
            tags_list.extend(t)
    num_tags = len(set(tags_list))

    # Database / image storage size
    db_file = Path("sb_data/db/notes.db")
    db_size = db_file.stat().st_size if db_file.exists() else 0

    images_path = Path("sb_data/images")
    num_images = len(list(images_path.glob("*.*"))) if images_path.exists() else 0
    images_size = sum(f.stat().st_size for f in images_path.glob("*.*")) if images_path.exists() else 0

    def format_size(b):
        for u in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.1f}{u}"
            b /= 1024
        return f"{b:.1f}TB"

    # Use a grid layout for rows and columns
    grid = QGridLayout()
    grid.setHorizontalSpacing(20)
    grid.setVerticalSpacing(10)

    stats = [
        ("Notes", num_notes),
        ("Categories", num_categories),
        ("Tags", num_tags),
        ("DB Size", format_size(db_size)),
        ("Images", f"{num_images} (Total {format_size(images_size)})")
    ]

    icon_paths = {
        "Notes": resource_path("resources/icons/notes.png"),
        "Categories": resource_path("resources/icons/category.png"),
        "Tags": resource_path("resources/icons/tag.png"),
        "DB Size": resource_path("resources/icons/db_pop.png"),
        "Images": resource_path("resources/icons/image_example.png")
    }

    for row, (label_text, value) in enumerate(stats):
        icon_label = QLabel()
        icon_pix = QPixmap(icon_paths.get(label_text, ""))  # fallback to empty
        if not icon_pix.isNull():
            icon_label.setPixmap(
                icon_pix.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        grid.addWidget(icon_label, row, 0)

        # Stat label
        label = QLabel(label_text + ":")
        label.setStyleSheet("color: #A8B9C8; font-weight: bold;")
        grid.addWidget(label, row, 1)

        # Value label
        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: #FFFFFF;")
        grid.addWidget(value_label, row, 2)

    db_layout.addLayout(grid)

    # Show dialog
    db_dialog.setLayout(db_layout)
    db_dialog.exec()  # modal dialog
