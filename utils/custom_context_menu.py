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
        """Shows a custom right-click context menu with Copy, Paste, Undo, Redo, and Select All."""

        context_menu = QMenu(self.widget)

        # Get standard context menu actions for the widget
        standard_menu = self.widget.createStandardContextMenu()

        # Check for available actions and add them to the custom context menu
        actions = standard_menu.actions()

        if len(actions) > 0:
            context_menu.addAction(actions[0])  # Copy
        if len(actions) > 1:
            context_menu.addAction(actions[1])  # Paste
        if len(actions) > 2:
            context_menu.addAction(actions[2])  # Undo
        if len(actions) > 3:
            context_menu.addAction(actions[3])  # Redo
        if len(actions) > 4:
            context_menu.addAction(actions[4])  # Select All

        # Add any other actions beyond the first 5, if available
        for i in range(5, len(actions)):
            context_menu.addAction(actions[i])

        # Optionally, set a custom stylesheet for the context menu
        context_menu.setStyleSheet(menu_style)

        # Execute the context menu at the requested position
        context_menu.exec(self.widget.mapToGlobal(pos))
