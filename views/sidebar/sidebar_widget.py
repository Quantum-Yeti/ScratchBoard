from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QFrame
from PySide6.QtCore import Signal, QSize, Qt, QUrl
import subprocess

from utils.resource_path import resource_path
from managers.scratch_manager import ScratchManager
from views.notepad_view import NotepadDialog


def open_github():
    """
    Open the ScratchBoard GitHub repository in the default web browser.
    This method uses `QDesktopServices.openUrl` to open the GitHub page for the
    ScratchBoard project. It launches the URL in the default web browser.
    """
    QDesktopServices.openUrl(QUrl("https://github.com/Quantum-Yeti/ScratchBoard"))


class Sidebar(QWidget):
    """
    The main sidebar widget for the application.

    This widget provides navigation buttons for the note categories, dashboard access, scratch pad,
    notepad, batch script execution, and the GitHub repository link. Signals are emitted when a category
    or the dashboard is selected.
    """
    # Emit signals for category selection + dashboard
    category_selected = Signal(str)
    dashboard_clicked = Signal()

    # Dictionary of categories with their icons
    CATEGORIES = {
        "Contacts": "resources/icons/contacts.png",
        "CoPilot": "resources/icons/copilot.png",
        "Internet": "resources/icons/internet.png",
        "Email": "resources/icons/email.png",
        "Phone": "resources/icons/landline.png",
        "Video": "resources/icons/video.png",
        "Streaming": "resources/icons/streaming.png",
        "Notes": "resources/icons/notes.png",
        "Ideas": "resources/icons/ideas.png",
    }

    # Dictionary of tooltips for each category
    CATEGORY_TOOLTIPS = {
        "Contacts": "View and manage your contacts",
        "CoPilot": "View and manage notes from your knowledge domain",
        "Internet": "View and manage your Internet notes",
        "Email": "View and manage your email notes",
        "Phone": "View and manage your phone notes",
        "Video": "View and manage your video notes",
        "Streaming": "View and manage your streaming notes",
        "Notes": "View and manage general notes",
        "Ideas": "View and manage your ideas",
    }

    def __init__(self, model=None):
        """
        Initialization of the Sidebar widget.
        :param model: Data model used by certain features such as the ScratchManager.
        """
        super().__init__()
        self.setObjectName("Sidebar")
        self.model = model

        # Main sidebar button layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Create category buttons dynamically
        for name, icon_file in Sidebar.CATEGORIES.items():
            btn = QPushButton(name)
            btn.setIcon(QIcon(resource_path(icon_file)))
            btn.setIconSize(QSize(32, 32))
            btn.setCursor(Qt.PointingHandCursor)

            # Initialize and set category tooltips
            cat_tooltips = Sidebar.CATEGORY_TOOLTIPS.get(name, "")
            btn.setToolTip(cat_tooltips)

            # Connect button click to emit category_selected signal
            btn.clicked.connect(lambda checked, c=name: self.category_selected.emit(c))
            layout.addWidget(btn)

            # Add visual separators between certain categories
            if name == "CoPilot" or name == "Streaming":
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)  # Horizontal line
                separator.setFrameShadow(QFrame.Plain)  # Gives subtle 3D effect
                separator.setStyleSheet("""
                    QFrame {
                        background-color: #2E2E2E;
                        color: #2e2e2e;
                    }
                """)
                separator.setFixedHeight(4)  # Thin line
                layout.addWidget(separator)

        # Stretch moves non-category buttons to bottom
        layout.addStretch()

        # Dashboard button
        dash_btn = QPushButton("Dashboard")
        dash_btn.setToolTip("View the dashboard")
        dash_btn.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        dash_btn.setIconSize(QSize(32, 32))
        dash_btn.setCursor(Qt.PointingHandCursor)
        dash_btn.clicked.connect(lambda: self.dashboard_clicked.emit())
        layout.addWidget(dash_btn)

        # Scratch pad button
        self.scratch_btn = QPushButton("Scratch Pad")
        self.scratch_btn.setToolTip("Open Scratch Pad to create sticky notes")
        self.scratch_btn.setIcon(QIcon(resource_path("resources/icons/scratch.png")))
        self.scratch_btn.setIconSize(QSize(32, 32))
        self.scratch_btn.setCursor(Qt.PointingHandCursor)
        self.scratch_btn.clicked.connect(self.open_scratch_pad)
        layout.addWidget(self.scratch_btn)

        # Notepad button
        note_btn = QPushButton("Notepad")
        note_btn.setToolTip("Open Notepad")
        note_btn.setIcon(QIcon(resource_path("resources/icons/notepad.png")))
        note_btn.setIconSize(QSize(32, 32))
        note_btn.setCursor(Qt.PointingHandCursor)
        note_btn.clicked.connect(self.open_notepad)
        layout.addWidget(note_btn)

        # Execute batch file button
        bat_btn = QPushButton("Execute Script")
        bat_btn.setToolTip("Select and run a batch file")
        bat_btn.setIcon(QIcon(resource_path("resources/icons/run.png")))
        bat_btn.setIconSize(QSize(32, 32))
        bat_btn.setCursor(Qt.PointingHandCursor)
        bat_btn.clicked.connect(self.open_bat_file)
        #layout.addWidget(bat_btn)

        # GitHub repository button
        logo_btn = QPushButton("Review Code")
        logo_btn.setToolTip("Visit the project repository on GitHub")
        logo_btn.setIcon(QIcon(resource_path("resources/icons/dev_logo.png")))
        logo_btn.setIconSize(QSize(32, 32))
        logo_btn.setFlat(True)
        logo_btn.setCursor(Qt.PointingHandCursor)
        logo_btn.clicked.connect(open_github)
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

    def open_notepad(self):
        """
        Method to open the Notepad dialog window.
        If an instance already exists, it is raised, otherwise it creates a new one.
        """
        if hasattr(self, "_notepad") and self._notepad:
            if self._notepad.isVisible():
                if self._notepad.isMinimized():
                    self._notepad.showNormal()  # restore if minimized
                self._notepad.raise_()
                self._notepad.activateWindow()
                return

        # Create a new dialog if none exists
        self._notepad = NotepadDialog(self.parent())
        self._notepad.show()
