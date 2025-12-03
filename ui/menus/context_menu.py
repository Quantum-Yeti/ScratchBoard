from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTextEdit

from utils.resource_path import resource_path


class ModifyContextMenu(QTextEdit):
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        icon_map = {
            "cut": "cut_small.png",
            "copy": "copy_small.png",
            "paste": "paste_small.png",
            "undo": "undo_small.png",
            "redo": "redo_small.png",
        }

        for action in menu.actions():
            text = action.text().lower()
            for key, icon in icon_map.items():
                if text.startswith(key):
                    action.setIcon(QIcon(resource_path(f"resources/icons/{icon}")))

        menu.exec_(event.globalPos())