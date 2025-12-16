import sys

from PySide6.QtCore import QSharedMemory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication,
                               QMainWindow,
                               QHBoxLayout,
                               QWidget,
                               QStackedLayout,
                               QMessageBox)
from helpers.start_helpers.run_startup import run_startup
from helpers.ui_helpers.update_window_title import update_window_title
from ui.menus.menu_bar import MainMenuBar
from views.splash.splash_screen import SplashScreen
from views.dashboard_view import DashboardView
from views.sidebar.sidebar_widget import Sidebar
from views.notes.main_note_view import MainView
from views.contacts.contacts_view import ContactsView
from controllers.note_controller import NoteController
from controllers.contacts_controller import ContactsController
from models.note_model import NoteModel
from utils.resource_path import resource_path

def load_styles(app):
    """
    This function loads and applies the global dark theme stylesheet.

    The QSS file is read from the ui/themes resource directory and applies
    it to the entire application. If the stylesheet fails to load, an exception
    is thrown and prints the error message to the console, but execution continues.

    Parameters:
        app (QApplication): The QApplication instance that the stylesheet is applied to.
    """
    try:
        with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Failed to load stylesheet:", e)

class MainWindow(QMainWindow):
    """
    This is the primary application window for Scratch Board.

    This class sets up the main user interface:
        - Window properties (titles, icons, sizes)
        - Sidebar with category navigation
        - Main views: Dashboard, Contacts, and Notes
        - Controllers: Notes and Contacts
        - Menu bar
        - Stacked layout
        - Dashboard refresh when note data for the categories changes

    The MainWindow coordinates interactions between models, views, and controllers,
    and manages the initial display of the Dashboard as the default view.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Scratch Board")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setGeometry(100, 100, 1280, 900)

        # Initialize dynamic window titles
        update_window_title(self)

        # Initialize application data models
        self.model = NoteModel()

        # Instantiate primary UI views
        categories = ["Contacts", "CoPilot", "Internet", "Email", "Phone", "Video", "Streaming", "Coaching", "Notes", "Ideas"]
        self.main_view = MainView(categories)
        self.contacts_view = ContactsView(categories)

        # Connect sidebar to model and pass signals
        self.sidebar = Sidebar(model=self.model)
        self.sidebar.category_selected.connect(self.on_sidebar_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        # Initialize dashboard view + connect to sidebar signal and data model
        self.dashboard_view = DashboardView(self.model, self.sidebar, image_path="resources/icons/astronaut_banner.png")

        # Bind controllers to their data models and views
        self.note_controller = NoteController(self.model, self.main_view, self.sidebar)
        self.contacts_controller = ContactsController(self.model, self.contacts_view, self.sidebar)

        # Initialize the menu bar
        self.menu_bar = MainMenuBar(self, model=self.model)
        self.menu_bar.set_sidebar(self.sidebar)
        self.setMenuBar(self.menu_bar)

        # Configure main window layout with stacked content
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

        # Refresh dashboard when note data updates
        self.note_controller.data_changed.connect(self.dashboard_view.refresh_dashboard)

        # Configure dashboard as initial view
        self.stacked_layout.setCurrentWidget(self.dashboard_view)

    # Sidebar handlers
    def on_sidebar_category_selected(self, category):
        """
        This method is called when the sidebar category is selected by the user.

        The window title is updated, the stacked layout switches to the appropriate
        view, and the data is refreshed for the selected category.

        *Important: All note-taking related categories rely on main_view and contacts has its own contacts_view.

        Parameters:
            category (str): The category selected by the user in the sidebar.
        """
        # Updates the window title based on selection
        update_window_title(self, category)

        # If contacts is selected, displays contacts view
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
        """
        This function displays the Dashboard view and refreshes its data. It updates
        the stacked layout to show the Dashboard and refreshes all dashboard widgets.
        """
        self.stacked_layout.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh_dashboard()

        update_window_title(self)

def main():
    """
    Main entry point for the Scratch Board application.

    This function initializes the Qt-based application as follows:
        1. Create the QApplication instance.
        2. Apply global QSS styles.
        3. Prevent multiple concurrent instances of the program using QSharedMemory.
        4. Display the splash screen and run start_helpers initialization.
        5. Initialize and display the main application window when the splash screen is finished.
        6. Start the Qt event loop.

    Exits:
        - Terminates immediately if another instance of the program is already running.
    """
    # Main Qt application instance handling event loop and GUI behavior
    app = QApplication(sys.argv)

    # Load and apply the global QSS stylesheet
    load_styles(app)

    # Prevent multiple instances of the application using a shared memory lock
    shared_mem = QSharedMemory("ScratchBoardAppInstance")
    if not shared_mem.create(1):
        QMessageBox.warning(None, "Already Running", "Scratch Board is already running.")
        sys.exit(0)

    # Initialize and run the start_helpers splash screen
    splash = SplashScreen(resource_path("resources/icons/astronaut_splash.png"))
    run_startup(splash.set_progress)

    # Initialize and display the main application window
    window = MainWindow()

    # Transition from splash screen to the fully initialized main window (order is important)
    splash.close()  # 1. Close the splash screen before showing the main window
    window.show()  # 2. Display the main application window
    window.raise_()  # 3. Ensure the window appears above all other windows
    window.activateWindow()  # 4. Give the window keyboard focus and activates it

    # Execute the Qt application loop and terminate the program when the window is closed
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
