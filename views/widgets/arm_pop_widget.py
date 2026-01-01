from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from pathlib import Path

from utils.custom_context_menu import ContextMenuUtility
from utils.resource_path import resource_path
from ui.themes.dash_action_btn_style import dash_action_button_style
from ui.themes.scrollbar_style import vertical_scrollbar_style

# Keep a global reference so the dialog doesn't close immediately
arm_pop_window = None

class ArmDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scratch Board: ARM Statement")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Read-only ARM text
        self.arm_text = QTextEdit()
        self.arm_text.setReadOnly(True)
        self.arm_text.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
        layout.addWidget(self.arm_text, stretch=1)

        self.context_menu_helper = ContextMenuUtility(self.arm_text)

        # Calls the function to load the arm statement
        self.load_arm()

    def load_arm(self):
        try:
            with open("sb_data/notepad/arm_statement.txt", "r", encoding="utf-8") as f:
                self.arm_text.setPlainText(f.read())
        except FileNotFoundError:
            self.arm_text.setPlainText("[No ARM statement found]")

# Non-modal pop-up function
def open_arm_pop():
    global arm_pop_window
    if arm_pop_window is None or not arm_pop_window.isVisible():
        arm_pop_window = ArmDialog()
    arm_pop_window.show()
    arm_pop_window.raise_()
    arm_pop_window.activateWindow()
