from PySide6.QtWidgets import QTextEdit

from ui.themes.menu_theme import menu_style
from helpers.ui_helpers.menu_hover_tip import HoverToolTip

class ModifyContextMenu(QTextEdit):
    """
    UI helper for modifying the context menu in a QTextEdit.
    """
    def contextMenuEvent(self, event):

        # Create the standard context menu
        menu = self.createStandardContextMenu()

        # Apply a stylesheet to the menu
        menu.setStyleSheet(menu_style)

        # Iterate  over a copy of the menu's  actions
        for action in list(menu.actions()):

            if not action.isEnabled():
                # Remove disabled actions from the menu
                menu.removeAction(action)
            else:
                # Set a tooltip for enabled actions that match text
                action.setToolTip(action.text())

        # Install event filter to handle hover tooltips
        menu.installEventFilter(HoverToolTip(menu))

        # Show the menu at global position for right-click event
        menu.exec_(event.globalPos())