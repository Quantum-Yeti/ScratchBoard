from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar

class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- File Menu ----
        file_menu = self.addMenu("File")
        file_menu.setToolTip("File Menu")

        # New Note
        self.new_action = QAction("New Note", self)
        self.new_action.setToolTip("New Note")
        self.new_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_action)

        # Import Action
        self.import_action = QAction("Import Notes", self)
        self.import_action.setToolTip("Import Notes")
        file_menu.addAction(self.import_action)
        self.import_action.setShortcut("Ctrl+I")
        file_menu.addAction(self.import_action)

        # Export Notes
        self.export_action = QAction("Export Notes", self)
        self.export_action.setToolTip("Export Notes")
        self.export_action.setShortcut("Ctrl+E")
        file_menu.addAction(self.export_action)

        # Exit
        self.exit_action = QAction("Exit", self)
        self.exit_action.setToolTip("Exit application")
        self.exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(self.exit_action)

        # ---- Edit Menu ----
        edit_menu = self.addMenu("Edit")
        edit_menu.setToolTip("Edit Menu")

        # Copy Action
        self.copy_action = QAction("Copy", self)
        self.copy_action.setToolTip("Copy")
        edit_menu.addAction(self.copy_action)

        # Paste action
        self.paste_action = QAction("Paste", self)
        self.paste_action.setToolTip("Paste")
        edit_menu.addAction(self.paste_action)

        # Preferences
        self.pref_action = QAction("Preferences", self)
        self.pref_action.setToolTip("Preferences")
        edit_menu.addAction(self.pref_action)

        # -- Tool Menu --
        tool_menu = self.addMenu("Tools")
        tool_menu.setToolTip("Tool Menu")

        self.dash_action = QAction("Dashboard", self)
        self.dash_action.setToolTip("Dashboard")
        tool_menu.addAction(self.dash_action)

        self.scratch_action = QAction("Scratch Board", self)
        self.scratch_action.setToolTip("Scratch Board")
        tool_menu.addAction(self.scratch_action)

        self.bat_action = QAction("Run *.bat", self)
        self.bat_action.setToolTip("Run *.bat")
        tool_menu.addAction(self.bat_action)






        # ---- Help Menu ----
        help_menu = self.addMenu("Help")
        self.about_action = QAction("About", self)
        help_menu.addAction(self.about_action)
