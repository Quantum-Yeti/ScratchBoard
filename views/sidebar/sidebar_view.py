from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QFrame
from PySide6.QtCore import Signal, QSize, Qt, QUrl
import subprocess
from utils.resource_path import resource_path
from managers.scratch_manager import ScratchManager
from views.notepad_view import NotepadDialog


class Sidebar(QWidget):
    category_selected = Signal(str)
    dashboard_clicked = Signal()

    def __init__(self, model=None):
        super().__init__()
        self.setObjectName("Sidebar")
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Note categories and their resource path to icons.
        self.categories = {
            "Contacts": "resources/icons/contacts.png",
            "CoPilot": "resources/icons/copilot.png",
            "Tasks": "resources/icons/tasks.png",
            "Projects": "resources/icons/projects.png",
            "Notes": "resources/icons/notes.png",
            "Ideas": "resources/icons/ideas.png",
            "Journal": "resources/icons/journal.png",
            "Personal": "resources/icons/personal.png"
        }

        for name, icon_file in self.categories.items():
            btn = QPushButton(name)
            btn.setIcon(QIcon(resource_path(icon_file)))
            btn.setIconSize(QSize(32, 32))
            btn.setCursor(Qt.PointingHandCursor)
            # lambda to captures name of the category
            btn.clicked.connect(lambda checked, c=name: self.category_selected.emit(c))
            layout.addWidget(btn)

            if name == "Projects":
                separator = QFrame()
                separator.setStyleSheet("background-color: #1F1F1F;")
                separator.setFrameShape(QFrame.StyledPanel)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setLineWidth(2)
                separator.setFixedHeight(15)
                layout.addWidget(separator)

        # Stretch moves buttons not related to category notes to the bottom.
        layout.addStretch()

        # Dashboard button
        dash_btn = QPushButton("Dashboard")
        dash_btn.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        dash_btn.setIconSize(QSize(32, 32))
        dash_btn.setCursor(Qt.PointingHandCursor)
        dash_btn.clicked.connect(lambda: self.dashboard_clicked.emit())
        layout.addWidget(dash_btn)

        # Scratch pad button
        self.scratch_btn = QPushButton("Scratch Pad")
        self.scratch_btn.setIcon(QIcon(resource_path("resources/icons/scratch.png")))
        self.scratch_btn.setIconSize(QSize(32, 32))
        self.scratch_btn.setCursor(Qt.PointingHandCursor)
        self.scratch_btn.clicked.connect(self.open_scratch_pad)
        layout.addWidget(self.scratch_btn)

        note_btn = QPushButton("Notepad")
        note_btn.setIcon(QIcon(resource_path("resources/icons/notepad.png")))
        note_btn.setIconSize(QSize(32, 32))
        note_btn.setCursor(Qt.PointingHandCursor)
        note_btn.clicked.connect(self._open_notepad)
        layout.addWidget(note_btn)

        # Run .bat button
        bat_btn = QPushButton("Run *.bat")
        bat_btn.setIcon(QIcon(resource_path("resources/icons/run.png")))
        bat_btn.setIconSize(QSize(32, 32))
        bat_btn.setCursor(Qt.PointingHandCursor)
        bat_btn.clicked.connect(self.open_bat_file)
        layout.addWidget(bat_btn)

        # GitHub logo button
        logo_btn = QPushButton("Review Code")
        logo_btn.setIcon(QIcon(resource_path("resources/icons/dev_logo.png")))
        logo_btn.setIconSize(QSize(32, 32))
        logo_btn.setFlat(True)
        logo_btn.setCursor(Qt.PointingHandCursor)
        logo_btn.clicked.connect(self.open_github)
        layout.addWidget(logo_btn, alignment=Qt.AlignBottom)

        # Keep track of scratch pad instance
        self._scratch_pad = None

    # Sidebar helper functions
    def open_scratch_pad(self):
        """
        Open the Scratch Pad window.
        If a Scratch Pad instance is already open and visible, this method brings it
        to the front instead of creating a new one. Otherwise, it creates a new
        ScratchManager window using the current model and displays it.
        Behavior:
            - Reuses an existing Scratch Pad if one is already open.
            - Ensures the Scratch Pad is raised and focused when reopened.
            - Creates and shows a new ScratchManager instance if none exists.
        Returns:
            None
        """
        if hasattr(self, "_scratch_pad") and self._scratch_pad and self._scratch_pad.isVisible():
            self._scratch_pad.raise_()
            return
        self._scratch_pad = ScratchManager(model=self.model)
        self._scratch_pad.show()

    def open_bat_file(self):
        """
        Open and execute a selected `.bat` file.
        This method opens a file dialog that allows the user to select a `.bat` file
        from the filesystem. If a valid file is selected, it attempts to execute the
        file using `subprocess.Popen`. If an error occurs during execution, the
        error is caught and printed to the console.
        Behavior:
            - Opens a file dialog to select a `.bat` file.
            - Executes the selected `.bat` file using `subprocess.Popen`.
            - Handles errors by printing an error message if the execution fails.
        Returns:
            None
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a *.bat file", "", "*.bat")
        if file_path:
            try:
                subprocess.Popen(file_path, shell=True)
            except Exception as e:
                print("Failed to run script:", e)

    def open_github(self):
        """
        Open the ScratchBoard GitHub repository in the default web browser.
        This method uses `QDesktopServices.openUrl` to open the GitHub page for the
        ScratchBoard project. It launches the URL in the default web browser.
        Returns:
            None
        """
        QDesktopServices.openUrl(QUrl("https://github.com/Quantum-Yeti/ScratchBoard"))

    def _open_notepad(self):
        dlg = NotepadDialog(self.parent())
        dlg.exec()  # modal dialog
