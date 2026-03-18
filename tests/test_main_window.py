import os
import pytest
from PySide6.QtWidgets import QApplication
from main import MainWindow, load_styles

# Run Qt in offscreen mode to avoid GUI crashes on Windows
os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="module")
def app():
    """Create a single QApplication instance for all tests in this module."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def main_window(app, qtbot):
    """Fixture to create and clean up MainWindow for each test."""
    window = MainWindow()
    qtbot.addWidget(window)  # Ensures proper cleanup
    yield window
    window.close()  # Close after test

def test_main_window_initialization(main_window):
    """Test that the main window initializes without errors."""
    window = main_window

    # Check basic properties
    assert window.windowTitle() == "Scratch Board"
    assert window.width() == 1280
    assert window.height() == 900

    # Check stacked layout has 3 widgets
    assert window.stacked_layout.count() == 3

    # Default view is dashboard
    current_widget = window.stacked_layout.currentWidget()
    assert current_widget == window.dashboard_view

def test_sidebar_category_selection(main_window):
    """Test switching views via sidebar."""
    window = main_window

    # Simulate selecting Contacts category
    window.on_sidebar_category_selected("Contacts")
    assert window.stacked_layout.currentWidget() == window.contacts_view

    # Simulate selecting Notes category
    window.on_sidebar_category_selected("Notes")
    assert window.stacked_layout.currentWidget() == window.main_view

    # Simulate selecting a random category
    window.on_sidebar_category_selected("Internet")
    assert window.stacked_layout.currentWidget() == window.main_view