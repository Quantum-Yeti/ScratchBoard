import json
from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


def update_db_stats(model):
    db_dialog = QDialog()
    db_dialog.setWindowTitle("Database Stats")
    db_dialog.setMinimumSize(300, 200)

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

    stats_text = (
        f"Notes: {num_notes}\n"
        f"Categories: {num_categories}\n"
        f"Tags: {num_tags}\n"
        f"DB Size: {format_size(db_size)}\n"
        f"Images: {num_images} (Total {format_size(images_size)})"
    )

    stats_label = QLabel(stats_text)
    stats_label.setStyleSheet("color: black; font-weight: bold;")
    db_layout.addWidget(stats_label)

    # Show dialog
    db_dialog.setLayout(db_layout)
    db_dialog.exec()  # modal dialog