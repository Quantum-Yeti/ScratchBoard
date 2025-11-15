from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMenu, QApplication

class CopyableLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == copy_action:
            QApplication.clipboard().setText(self.text())
