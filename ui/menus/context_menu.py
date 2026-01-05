from PySide6.QtWidgets import QTextEdit

from ui.themes.menu_theme import menu_style
from helpers.ui_helpers.menu_hover_tip import HoverToolTip

class ModifyContextMenu(QTextEdit):
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        # Apply a stylesheet to the menu
        menu.setStyleSheet(menu_style)

        for action in list(menu.actions()):
            if not action.isEnabled():
                menu.removeAction(action)
            else:
                action.setToolTip(action.text())

        menu.installEventFilter(HoverToolTip(menu))

        menu.exec_(event.globalPos())