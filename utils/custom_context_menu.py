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

        standard_menu = self.widget.createStandardContextMenu()

        # Add Copy and Paste actions (use built-in actions from QTextEdit)
        copy_action = standard_menu.actions()[0]  # Copy
        paste_action = standard_menu.actions()[1]  # Paste
        undo_action = standard_menu.actions()[2]  # Undo
        redo_action = standard_menu.actions()[3]  # Redo
        select_all_action = standard_menu.actions()[4]  # Select All

        context_menu.addAction(copy_action)
        context_menu.addAction(paste_action)
        context_menu.addAction(undo_action)
        context_menu.addAction(redo_action)
        context_menu.addAction(select_all_action)

        context_menu.setStyleSheet(menu_style)

        # Execute the context menu at the requested position
        context_menu.exec(self.widget.mapToGlobal(pos))
