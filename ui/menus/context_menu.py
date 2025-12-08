from PySide6.QtWidgets import QTextEdit

from ui.themes.context_menu_theme import menu_style
from utils.menu_hover_tip import HoverToolTip

class ModifyContextMenu(QTextEdit):
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        # Apply a stylesheet to the menu
        menu.setStyleSheet(menu_style)

        for action in menu.actions():
            if not action.isEnabled():
                menu.removeAction(action)
            else:
                action.setToolTip(action.text())

        menu.installEventFilter(HoverToolTip(menu))

        menu.exec_(event.globalPos())