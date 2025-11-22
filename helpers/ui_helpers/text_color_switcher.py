from PySide6.QtGui import QColor


def get_text_color(bg_color):
    """Return black or white text depending on background brightness."""
    c = QColor(bg_color)
    brightness = (c.red()*299 + c.green()*587 + c.blue()*114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"