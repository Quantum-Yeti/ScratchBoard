# helpers/drag_drop_image.py
import os
import shutil
from pathlib import Path
from PySide6.QtGui import QPixmap

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

def ensure_image_dir() -> Path:
    dst_dir = Path(os.getcwd()) / "data" / "images"
    dst_dir.mkdir(parents=True, exist_ok=True)
    return dst_dir


def save_qimage(image) -> str | None:
    """Save an image from clipboard-drag data and return md_helpers path."""
    dst = ensure_image_dir()

    # Using a timestamp avoids collisions
    fname = dst / f"dropped_{os.times()[4]}.png"
    pm = QPixmap.fromImage(image) if hasattr(image, "save") else image
    pm.save(str(fname), "PNG")

    return format_markdown_reference(fname)


def save_file_drop(local_path: str) -> str | None:
    """Copy a dropped file into images folder and return md_helpers path."""
    if not Path(local_path).is_file():
        return None

    ext = Path(local_path).suffix.lower()
    if ext not in IMAGE_EXTS:
        return None

    dst_dir = ensure_image_dir()
    dst = dst_dir / Path(local_path).name

    # avoid overwriting existing filenames
    i = 1
    while dst.exists():
        dst = dst_dir / f"{Path(local_path).stem}_{i}{ext}"
        i += 1

    shutil.copy(local_path, dst)
    return format_markdown_reference(dst)


def format_markdown_reference(path: Path) -> str:
    rel = os.path.relpath(path, os.getcwd()).replace("\\", "/")
    return f"![image]({rel})"
