from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QStackedLayout
from views.dashboard import DashboardView
from views.sidebar import Sidebar
from views.main_view import MainView
from controllers.note_controller import NoteController
from models.note_model import NoteModel
from utils.resource_path import resource_path
import sys

def load_styles(app):
    with open(resource_path("ui/themes/dark.qss"), "r") as f:
        app.setStyleSheet(f.read())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScratchBoard")

        # Model
        self.model = NoteModel()

        # Views
        categories = ["Contacts", "Bookmarks", "CoPilot", "Notes"]
        self.main_view = MainView(categories)
        self.dashboard_view = DashboardView(self.model,
                                            image_path="resources/icons/penguin.png")

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.category_selected.connect(self.on_sidebar_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        # Layout
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

        # Controller (pass main_view only)
        self.controller = NoteController(self.model, self.main_view, self.sidebar)

        # Show main notes view by default
        self.stacked_layout.setCurrentWidget(self.dashboard_view)

    # --- Slot for sidebar category buttons ---
    def on_sidebar_category_selected(self, category):
        # Ensure note view is visible
        self.stacked_layout.setCurrentWidget(self.main_view)
        self.controller.current_category = category
        self.controller.refresh_notes()

    # --- Slot for dashboard button ---
    def show_dashboard(self):
        self.stacked_layout.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.update_graphs()

def main():
    app = QApplication(sys.argv)
    load_styles(app)
    window = MainWindow()
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
