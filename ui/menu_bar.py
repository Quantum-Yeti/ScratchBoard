from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtWidgets import QMenuBar, QToolTip, QApplication

from ui.themes.top_menu_theme import top_menu_style
from utils.resource_path import resource_path
from views.chart_widgets.fiber_chart import FiberReferenceDialog
from views.chart_widgets.signal_widget import SignalReference
from views.chart_widgets.ethernet_widget import EthernetReference
from views.chart_widgets.speed_widget import InternetSpeedRequirements
from views.widgets.log_widget import ModemLogParserView
from views.notepad_view import NotepadDialog
from views.widgets.about_widget import AboutWidget
from views.chart_widgets.wifi_standards_widget import WifiStandardsReference
from views.widgets.md_widget import MarkdownGuideWidget


# Internal tooltip hover function
def _connect_hover_tooltips(menu):
    """
    Connect hover events for all actions in the given menu to display
    their associated tooltips.

    This method iterates through each QAction in the provided menu and,
    for those that define a tooltip, connects the `hovered` signal to a
    handler that displays the tooltip at the current cursor position.
    This enables on-hover tooltip behavior within menus.
    """
    for action in menu.actions():
        if action.toolTip():
            action.hovered.connect(
                lambda a=action: QToolTip.showText(QCursor.pos(), a.toolTip())
            )


class MainMenuBar(QMenuBar):
    """
    Main application menu bar.

    Initializes the menu bar, applies custom styling, defines all action
    placeholders, and constructs the menus.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # init actions to avoid attribute errors before menus are built
        self.import_action = None
        self.export_action = None
        self.exit_action = None
        self.dash_action = None
        self.scratch_action = None
        self.bat_action = None
        self.modem_action = None
        self.signal_action = None
        self.ethernet_action = None
        self.speeds_action = None
        self.fiber_action = None
        self.contact_action = None
        self.tasks_action = None
        self.project_action = None
        self.about_action = None
        self.md_action = None

        # Build menus
        self._build_file_menu()
        self._build_tools_menu()
        self._build_views_menu()
        self._build_charts_menu()
        self._build_help_menu()

        # Initialize the sidebar for the categories
        self.sidebar = None

        # Override the dark_theme.qss and apply a hover color to menus via QSS
        self.setStyleSheet(top_menu_style)

    # Build the File menu
    def _build_file_menu(self):
        file_menu = self.addMenu("File")

        self.import_action = QAction("Import Notes", self)
        self.import_action.setIcon(QIcon(resource_path("resources/icons/import.png")))
        file_menu.addAction(self.import_action)

        self.export_action = QAction("Export Notes", self)
        self.export_action.setIcon(QIcon(resource_path("resources/icons/export.png")))
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setIcon(QIcon(resource_path("resources/icons/exit.png")))
        file_menu.addAction(self.exit_action)

        self.exit_action.triggered.connect(QApplication.instance().quit)

        # Hover tooltips
        _connect_hover_tooltips(file_menu)

    # Build the tools menu
    def _build_tools_menu(self):
        tools_menu = self.addMenu("Tools")

        self.dash_action = QAction("Dashboard", self)
        self.dash_action.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        self.dash_action.setShortcut("F10")
        tools_menu.addAction(self.dash_action)

        self.scratch_action = QAction("Scratch Note", self)
        self.scratch_action.setIcon(QIcon(resource_path("resources/icons/stickynote.png")))
        self.scratch_action.setShortcut("F11")
        tools_menu.addAction(self.scratch_action)

        self.notepad_action = QAction("Notepad", self)
        self.notepad_action.setIcon(QIcon(resource_path("resources/icons/notepad.png")))
        self.notepad_action.setShortcut("F12")
        tools_menu.addAction(self.notepad_action)

        self.bat_action = QAction("Run *.bat", self)
        self.bat_action.setIcon(QIcon(resource_path("resources/icons/run.png")))
        self.bat_action.setShortcut("Ctrl+B")
        tools_menu.addAction(self.bat_action)

        tools_menu.addSeparator()

        self.modem_action = QAction("Log Parser", self)
        self.modem_action.setIcon(QIcon(resource_path("resources/icons/network.png")))
        self.modem_action.setShortcut("Ctrl+L")
        tools_menu.addAction(self.modem_action)

        _connect_hover_tooltips(tools_menu)

    def _build_charts_menu(self):
        charts_menu = self.addMenu("Charts")

        self.signal_action = QAction("DOCSIS Signal Chart", self)
        self.signal_action.setIcon(QIcon(resource_path("resources/icons/signal.png")))
        self.signal_action.setShortcut("Ctrl+P")
        charts_menu.addAction(self.signal_action)

        self.fiber_action = QAction("Fiber Signal Chart", self)
        self.fiber_action.setIcon(QIcon(resource_path("resources/icons/fiber.png")))
        self.fiber_action.setShortcut("Ctrl+Z")
        charts_menu.addAction(self.fiber_action)

        self.ethernet_action = QAction("Ethernet Standards Chart", self)
        self.ethernet_action.setIcon(QIcon(resource_path("resources/icons/ethernet.png")))
        self.ethernet_action.setShortcut("Ctrl+E")
        charts_menu.addAction(self.ethernet_action)

        self.wifi_standards_action = QAction("WiFi Standards Chart", self)
        self.wifi_standards_action.setIcon(QIcon(resource_path("resources/icons/wifi.png")))
        self.wifi_standards_action.setShortcut("Ctrl+W")
        charts_menu.addAction(self.wifi_standards_action)

        self.speeds_action = QAction("Speed Chart", self)
        self.speeds_action.setIcon(QIcon(resource_path("resources/icons/speed.png")))
        self.speeds_action.setShortcut("Ctrl+W")
        charts_menu.addAction(self.speeds_action)

        _connect_hover_tooltips(charts_menu)

    # Build the View Menu
    def _build_views_menu(self):
        view_menu = self.addMenu("Views")

        self.contact_action = QAction("Contacts", self)
        self.contact_action.setIcon(QIcon(resource_path("resources/icons/contacts.png")))
        self.contact_action.setShortcut("F1")
        view_menu.addAction(self.contact_action)

        self.copilot_action = QAction("CoPilot", self)
        self.copilot_action.setIcon(QIcon(resource_path("resources/icons/owl.png")))
        self.copilot_action.setShortcut("F2")
        view_menu.addAction(self.copilot_action)

        self.tasks_action = QAction("Tasks", self)
        self.tasks_action.setIcon(QIcon(resource_path("resources/icons/tasks.png")))
        self.tasks_action.setShortcut("F3")
        view_menu.addAction(self.tasks_action)

        self.project_action = QAction("Projects", self)
        self.project_action.setIcon(QIcon(resource_path("resources/icons/projects.png")))
        self.project_action.setShortcut("F4")
        view_menu.addAction(self.project_action)

        self.notes_action = QAction("Notes", self)
        self.notes_action.setIcon(QIcon(resource_path("resources/icons/notes.png")))
        self.notes_action.setShortcut("F5")
        view_menu.addAction(self.notes_action)

        self.ideas_action = QAction("Ideas", self)
        self.ideas_action.setIcon(QIcon(resource_path("resources/icons/ideas.png")))
        self.ideas_action.setShortcut("F6")
        view_menu.addAction(self.ideas_action)

        self.journal_action = QAction("Journal", self)
        self.journal_action.setIcon(QIcon(resource_path("resources/icons/journal.png")))
        self.journal_action.setShortcut("F7")
        view_menu.addAction(self.journal_action)

        self.personal_action = QAction("Personal", self)
        self.personal_action.setIcon(QIcon(resource_path("resources/icons/personal.png")))
        self.personal_action.setShortcut("F8")
        view_menu.addAction(self.personal_action)

        _connect_hover_tooltips(view_menu)

    # Build the Help menu
    def _build_help_menu(self):
        help_menu = self.addMenu("Help")

        self.md_action = QAction("Markdown Quick Guide", self)
        self.md_action.setIcon(QIcon(resource_path("resources/icons/markdown.png")))
        help_menu.addAction(self.md_action)

        self.about_action = QAction("About", self)
        self.about_action.setIcon(QIcon(resource_path("resources/icons/about.png")))
        help_menu.addAction(self.about_action)

        _connect_hover_tooltips(help_menu)

    def set_sidebar(self, sidebar):
        """
        Connects the main window's actions to the corresponding handlers
        provided by the sidebar object.

        This method stores the given sidebar instance and wires all toolbar
        and menu actions so that user interaction in the main window delegates
        to the sidebar’s logic. It also emits category selection signals and
        opens auxiliary dialogs where appropriate.
        """
        # Initialize the sidebar for the category actions
        self.sidebar = sidebar

        # Wire dashboard view
        self.dash_action.triggered.connect(self.sidebar.dashboard_clicked) # show dashboard

        # Wire the tools
        self.scratch_action.triggered.connect(self.sidebar.open_scratch_pad) # open the scratch notes
        self.notepad_action.triggered.connect(self._open_notepad)
        self.bat_action.triggered.connect(self.sidebar.open_bat_file) # run a batch file
        self.modem_action.triggered.connect(self._open_modem_parser)

        # Wire the charts
        self.signal_action.triggered.connect(self._open_signal_chart)
        self.ethernet_action.triggered.connect(self._open_ethernet_chart)
        self.wifi_standards_action.triggered.connect(self._open_wifi_chart)
        self.speeds_action.triggered.connect(self._open_speed_chart)
        self.fiber_action.triggered.connect(self._open_fiber_chart)

        # Wire the view categories
        self.contact_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Contacts"))
        self.copilot_action.triggered.connect(lambda: self.sidebar.category_selected.emit("CoPilot"))
        self.tasks_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Tasks"))
        self.project_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Projects"))
        self.notes_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Notes"))
        self.ideas_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Ideas"))
        self.journal_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Journal"))
        self.personal_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Personal"))

        # Wire the help menu
        self.md_action.triggered.connect(self._open_md_guide)
        self.about_action.triggered.connect(lambda: AboutWidget().exec())

    # Internal Helpers: opens non-category menu items
    def _open_notepad(self):
        ntp = NotepadDialog(self.parent())
        ntp.exec()  # modal dialog

    def _open_modem_parser(self):
        mdm = ModemLogParserView(self.parent())
        mdm.exec()  # modal; blocks main window until closed

    def _open_signal_chart(self):
        sgnl = SignalReference(self.parent())
        sgnl.exec()

    def _open_ethernet_chart(self):
        eth = EthernetReference(self.parent())
        eth.exec()

    def _open_wifi_chart(self):
        wfi = WifiStandardsReference(self.parent())
        wfi.exec()

    def _open_speed_chart(self):
        spd = InternetSpeedRequirements(self.parent())
        spd.exec()

    def _open_fiber_chart(self):
        fbr = FiberReferenceDialog(self.parent())
        fbr.exec()

    def _open_md_guide(self):
        if not hasattr(self, '_md_widget'):
            self._md_widget = MarkdownGuideWidget()
        self._md_widget.show()
