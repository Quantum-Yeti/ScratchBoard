from PySide6.QtWidgets import QTextEdit

from utils.menu_hover_tip import HoverToolTip


class ModifyContextMenu(QTextEdit):
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        # Apply a stylesheet to the menu
        menu.setStyleSheet("""
            QMenu {
                background-color: #1f1f1f;
                color: #f0f0f0;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 24px;
            }
            QMenu::item:selected {
                background-color: #505050;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: #3c3c3c;
                margin: 4px 0px 4px 0px;
            }
        """)

        for action in menu.actions():
            if not action.isEnabled():
                menu.removeAction(action)
            else:
                action.setToolTip(action.text())

        menu.installEventFilter(HoverToolTip(menu))

        menu.exec_(event.globalPos())