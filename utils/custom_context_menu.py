from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import QObject, QEvent, Qt

from ui.themes.menu_theme import menu_style


class ContextMenuUtility:
    """Helper class to manage custom context menus for widgets like QTextEdit."""

    def __init__(self, widget):
        self.widget = widget
        self.widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.widget.customContextMenuRequested.connect(self.show_custom_context_menu)

    def show_custom_context_menu(self, pos):
        """Shows a custom right-click context menu with Copy and Paste."""
        context_menu = QMenu(self.widget)

        # Add Copy and Paste actions (use built-in actions from QTextEdit)
        copy_action = self.widget.createStandardContextMenu().actions()[0]  # Copy
        paste_action = self.widget.createStandardContextMenu().actions()[1]  # Paste

        context_menu.addAction(copy_action)
        context_menu.addAction(paste_action)

        context_menu.setStyleSheet(menu_style)

        # Execute the context menu at the requested position
        context_menu.exec(self.widget.mapToGlobal(pos))
