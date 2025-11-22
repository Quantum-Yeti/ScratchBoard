import sys
import os
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QPoint
from utils.resource_path import resource_path

class FloatingButton(QPushButton):
    def __init__(self, parent, icon_path="resources/icons/add.png", tooltip="Add", shortcut="Ctrl+N", size=50):
        super().__init__(parent)
        self.setObjectName("FloatingButton")
        self.setToolTip(f"{tooltip} ({shortcut})")
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)

        # Load icon
        icon = QIcon(resource_path(icon_path))
        self.setIcon(icon)
        self.setIconSize(self.size())  # Icon fills the button

        # Animation for hover lift
        self._anim = QPropertyAnimation(self, b"pos", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        # Event filter for parent resize & hover effects
        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

        # Keyboard shortcut
        self.shortcut = QShortcut(QKeySequence(shortcut), parent)
        self.shortcut.setContext(Qt.ApplicationShortcut)
        self.shortcut.activated.connect(self.click)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            self.reposition()
        elif obj == self and event.type() == QEvent.Enter:
            self._animate(lift=True)
        elif obj == self and event.type() == QEvent.Leave:
            self._animate(lift=False)
        return super().eventFilter(obj, event)

    def reposition(self, margin=20):
        parent = self.parent()
        if parent:
            x = parent.width() - self.width() - margin
            y = parent.height() - self.height() - margin
            self.move(x, y)
            self.raise_()

    def _animate(self, lift: bool):
        cur = self.pos()
        target = QPoint(cur.x(), cur.y() - 4 if lift else cur.y() + 4)
        self._anim.stop()
        self._anim.setStartValue(cur)
        self._anim.setEndValue(target)
        self._anim.start()
