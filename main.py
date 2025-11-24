import sys

from PySide6.QtCore import QSharedMemory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QHBoxLayout,
                               QWidget,
                               QStackedLayout,
                               QMessageBox)

from helpers.startup.run_startup import run_startup
from helpers.ui_helpers.update_window_title import update_window_title
from ui.menu_bar import MainMenuBar
from views.splash.splash_screen import SplashScreen
from views.dashboard_view import DashboardView
from views.sidebar.sidebar_view import Sidebar
from views.main_view import MainView
from views.contacts_view import ContactsView
from controllers.note_controller import NoteController
from controllers.contacts_controller import ContactsController
from models.note_model import NoteModel
from utils.resource_path import resource_path

def load_styles(app):
    """Load dark theme QSS globally."""
    try:
        with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Failed to load stylesheet:", e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Scratch Board")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setGeometry(100, 100, 1280, 900)

        # Update window title
        update_window_title(self)

        # Model
        self.model = NoteModel()

        # Views
        categories = ["Contacts", "CoPilot", "Internet", "Phone", "Video", "Streaming", "Notes", "Ideas"]
        self.main_view = MainView(categories)
        self.contacts_view = ContactsView(categories)

        # Sidebar
        self.sidebar = Sidebar(model=self.model)
        self.sidebar.category_selected.connect(self.on_sidebar_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        # Dashboard
        self.dashboard_view = DashboardView(self.model, self.sidebar, image_path="resources/icons/penguin.png")

        # Controllers
        self.note_controller = NoteController(self.model, self.main_view, self.sidebar)
        self.contacts_controller = ContactsController(self.model, self.contacts_view, self.sidebar)

        # Menu bar
        self.menu_bar = MainMenuBar(self, model=self.model)
        self.menu_bar.set_sidebar(self.sidebar)
        self.setMenuBar(self.menu_bar)

        # Layout
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.main_view)       # index 0
        self.stacked_layout.addWidget(self.dashboard_view)  # index 1
        self.stacked_layout.addWidget(self.contacts_view)   # index 2

        layout.addWidget(self.sidebar)
        layout.addLayout(self.stacked_layout)
        self.setCentralWidget(container)

        # Connect note changes to dashboard
        self.note_controller.data_changed.connect(self.dashboard_view.refresh_dashboard)

        # Show dashboard by default
        self.stacked_layout.setCurrentWidget(self.dashboard_view)

    # Sidebar handlers
    def on_sidebar_category_selected(self, category):
        update_window_title(self, category)

        if category == "Contacts":
            self.stacked_layout.setCurrentWidget(self.contacts_view)
            self.contacts_controller.refresh_contacts()
        elif category == "Notes":
            self.stacked_layout.setCurrentWidget(self.main_view)
            self.note_controller.current_category = category
            self.note_controller.refresh_notes()
        else:
            # For other categories, default to main view
            self.stacked_layout.setCurrentWidget(self.main_view)
            self.note_controller.current_category = category
            self.note_controller.refresh_notes()

    def show_dashboard(self):
        self.stacked_layout.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh_dashboard()

        update_window_title(self)

def main():
    app = QApplication(sys.argv)
    load_styles(app)

    # Ensure only one instance of the program runs using QSharedMemory method
    shared_mem = QSharedMemory("ScratchBoardAppInstance")
    if not shared_mem.create(1):
        QMessageBox.warning(None, "Already Running", "Scratch Board is already running.")
        sys.exit(0)

    # Splash screen
    splash = SplashScreen(resource_path("resources/icons/astronaut_splash.png"))
    run_startup(splash)

    # Main window
    window = MainWindow()

    splash.close()  # hide splash first
    window.show()  # show main window
    window.raise_()  # bring to front
    window.activateWindow()  # give keyboard focus

    #update_dialog = UpdateDialog()
    #update_dialog.exec()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
