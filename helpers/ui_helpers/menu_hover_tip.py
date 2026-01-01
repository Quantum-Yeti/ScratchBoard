from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QToolTip, QMenu


class HoverToolTip(QObject):
    """Event filter that displays tooltips for QMenu actions when hovering with a mouse."""
    def eventFilter(self, obj, event):
        """
        Intercepts events for QMenu actions when hovering with a mouse.
        :param obj: QMenu object that receives the event.
        :param event: The event object to filter.
        :return: boolean: True if the event was handled (display/hide), False otherwise.
        """
        if isinstance(obj, QMenu) and event.type() == QEvent.Type.ToolTip:
            action = obj.actionAt(event.pos())
            if action and action.toolTip():
                QToolTip.showText(event.globalPos(), action.toolTip())
            else:
                QToolTip.hideText()
            return True
        return super().eventFilter(obj, event)