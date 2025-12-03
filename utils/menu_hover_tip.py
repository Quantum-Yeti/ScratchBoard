from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QToolTip, QMenu


class HoverToolTip(QObject):
    def eventFilter(self, obj, event):
        if isinstance(obj, QMenu) and event.type() == QEvent.ToolTip:
            action = obj.actionAt(event.pos())
            if action and action.toolTip():
                QToolTip.showText(event.globalPos(), action.toolTip())
            else:
                QToolTip.hideText()
            return True
        return super().eventFilter(obj, event)