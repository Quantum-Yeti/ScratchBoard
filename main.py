
import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QStackedLayout

from helpers.run_startup import run_startup
from ui.menu_bar import MainMenuBar
from views.splash_screen import SplashScreen
from views.dashboard import DashboardView
from views.sidebar import Sidebar
from views.main_view import MainView
from controllers.note_controller import NoteController
from models.note_model import NoteModel
from utils.resource_path import resource_path, configure_matplotlib


def load_styles(app):
    """Load the dark theme stylesheet."""
    with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
        app.setStyleSheet(f.read())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScratchBoard")
        self.setWindowIcon(QIcon(resource_path("resources/icons/astronaut.ico")))
        self.setGeometry(200, 200, 800, 600)

        # --- Model ---
        self.model = NoteModel()

        # --- Views ---
        categories = ["Contacts", "Bookmarks", "CoPilot", "Notes"]
        self.main_view = MainView(categories)
        self.dashboard_view = DashboardView(self.model, image_path="resources/icons/penguin.png")

        # --- Sidebar ---
        self.sidebar = Sidebar(model=self.model)
        self.sidebar.category_selected.connect(self.on_sidebar_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        # Menu
        menu_bar = MainMenuBar(self)
        self.setMenuBar(menu_bar)


        # --- Layout ---
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        # Stacked layout for main content
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.main_view)       # index 0
        self.stacked_layout.addWidget(self.dashboard_view)  # index 1

        layout.addWidget(self.sidebar)
        layout.addLayout(self.stacked_layout)
        self.setCentralWidget(container)

        # --- Controller ---
        self.controller = NoteController(self.model, self.main_view, self.sidebar)

        # Connect controller's data_changed signal to dashboard refresh
        self.controller.data_changed.connect(self.dashboard_view.refresh_dashboard)

        # Show main notes view by default
        self.stacked_layout.setCurrentWidget(self.dashboard_view)

    # --- Sidebar category buttons ---
    def on_sidebar_category_selected(self, category):
        self.stacked_layout.setCurrentWidget(self.main_view)
        self.controller.current_category = category
        self.controller.refresh_notes()

    # --- Dashboard button ---
    def show_dashboard(self):
        self.stacked_layout.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh_dashboard()


def main():
    app = QApplication(sys.argv)

    configure_matplotlib()  # needed for PyInstaller

    load_styles(app)

    # --- Splash Screen ---
    splash = SplashScreen(resource_path("resources/icons/astronautsplash.png"))
    run_startup(splash)

    # --- Window settings ---
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    splash.close()

    sys.exit(app.exec())


# Program entry
if __name__ == "__main__":
    main()
