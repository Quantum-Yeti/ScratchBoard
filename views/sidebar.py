import subprocess
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QPlainTextEdit
from PySide6.QtCore import Signal, QSize, Qt, QUrl
from views.scratch_view import ScratchPad
from utils.resource_path import resource_path

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

        self.categories = {
            "Contacts": "resources/icons/contacts.png",
            "Bookmarks": "resources/icons/bookmarks.png",
            "CoPilot": "resources/icons/copilot.png",
            "Notes": "resources/icons/notes.png",
        }

        for name, icon_file in self.categories.items():
            btn = QPushButton(name)
            btn.setIcon(QIcon(resource_path(icon_file)))
            btn.setIconSize(QSize(32, 32))
            btn.clicked.connect(lambda checked, c=name: self.category_selected.emit(c))
            layout.addWidget(btn)

        layout.addStretch()

        dash_btn = QPushButton("Dashboard")
        dash_btn.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        dash_btn.setIconSize(QSize(32, 32))
        dash_btn.clicked.connect(lambda: self.dashboard_clicked.emit())
        layout.addWidget(dash_btn)

        self.scratch_btn = QPushButton("Scratch Pad")
        self.scratch_btn.setIcon(QIcon(resource_path("resources/icons/scratch.png")))
        self.scratch_btn.setIconSize(QSize(32, 32))
        self.layout().addWidget(self.scratch_btn)
        self.scratch_btn.clicked.connect(self.open_scratch_pad)

        bat_btn = QPushButton("Run *.bat")
        bat_btn.setIcon(QIcon(resource_path("resources/icons/run.png")))
        bat_btn.setIconSize(QSize(32, 32))
        bat_btn.clicked.connect(self.open_bat_file)
        layout.addWidget(bat_btn)

        logo_btn = QPushButton("Review Code")
        logo_btn.setIcon(QIcon(resource_path("resources/icons/dev_logo.png")))
        logo_btn.setIconSize(QSize(32, 32))
        logo_btn.setFlat(True)
        #logo_btn.setEnabled(False)
        logo_btn.setCursor(Qt.PointingHandCursor)
        logo_btn.clicked.connect(self.open_github)
        layout.addWidget(logo_btn, alignment=Qt.AlignBottom)

    def open_bat_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a *.bat file", "", "*.bat")
        if file_path:
            try:
                subprocess.Popen(file_path, shell=True)
            except Exception as e:
                print("Failed to run script:", e)

    def open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/Quantum-Yeti/ScratchBoard"))


    def open_scratch_pad(self):
        if hasattr(self, "_scratch_pad") and self._scratch_pad.isVisible():
            self._scratch_pad.raise_()
            return
        self._scratch_pad = ScratchPad(parent=self, model=self.model)
        self._scratch_pad.show()
