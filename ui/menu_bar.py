from PySide6.QtGui import QAction, QCursor, QIcon, Qt
from PySide6.QtWidgets import QMenuBar, QToolTip, QApplication

from utils.resource_path import resource_path
from views.docsis_signal_view import SignalReference
from views.modem_log_view import ModemLogParserView
from views.widgets.about_widget import AboutWidget


class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply hover color to menus via QSS
        self.setStyleSheet("""
            QMenu::item:selected {
                background-color: #505050;  /* Slight change on hover */
            }
        """)

        # Initialize sidebar
        self.sidebar = None

        # File Menu
        file_menu = self.addMenu("File")
        file_menu.setObjectName("FileMenu")
        file_menu.setToolTip("File Menu")

        # TODO: implement import of SQLite db
        # Import database action
        self.import_action = QAction("Import Notes", self)
        self.import_action.setToolTip("Import Database")
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.setIcon(QIcon(resource_path("resources/icons/import.png")))
        file_menu.addAction(self.import_action)

        # TODO: implement export of SQLite db
        # Export database action
        self.export_action = QAction("Export Notes", self)
        self.export_action.setToolTip("Export Database")
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setIcon(QIcon(resource_path("resources/icons/export.png")))
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        # Exit action
        self.exit_action = QAction("Exit", self)
        self.exit_action.setToolTip("Exit application")
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setIcon(QIcon(resource_path("resources/icons/exit.png")))
        file_menu.addAction(self.exit_action)

        # Wire actions
        self.exit_action.triggered.connect(lambda: QApplication.instance().quit()) # quit application

        # Connect mouse hover events for file menu
        for action in file_menu.actions():
            action.hovered.connect(lambda act=action: QToolTip.showText(QCursor.pos(), act.toolTip()))

        # Tools Menu
        tool_menu = self.addMenu("Tools")
        tool_menu.setObjectName("ToolMenu")
        tool_menu.setToolTip("Tool Menu")

        # Dashboard action
        self.dash_action = QAction("Dashboard", self)
        self.dash_action.setToolTip("Dashboard")
        self.dash_action.setShortcut("Ctrl+D")
        self.dash_action.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        tool_menu.addAction(self.dash_action)

        # Scratch notes action
        self.scratch_action = QAction("Scratch Note", self)
        self.scratch_action.setToolTip("Scratch Note")
        self.scratch_action.setShortcut("Ctrl+B")
        self.scratch_action.setIcon(QIcon(resource_path("resources/icons/stickynote.png")))
        tool_menu.addAction(self.scratch_action)

        # Run a batch file action
        self.bat_action = QAction("Run *.bat", self)
        self.bat_action.setToolTip("Run *.bat")
        self.bat_action.setShortcut("Ctrl+R")
        self.bat_action.setIcon(QIcon(resource_path("resources/icons/run.png")))
        tool_menu.addAction(self.bat_action)

        # Modem log parser
        self.modem_action = QAction("Modem Log Parser", self)
        self.modem_action.setToolTip("Modem Log Parser")
        self.modem_action.setShortcut("Ctrl+M")
        self.modem_action.setIcon(QIcon(resource_path("resources/icons/network.png")))
        tool_menu.addAction(self.modem_action)

        # DOCSIS Signal Reference
        self.docsis_action = QAction("DOCSIS Signal Reference", self)
        self.docsis_action.setToolTip("DOCSIS Signal Reference")
        self.docsis_action.setShortcut("Ctrl+D")
        self.docsis_action.setIcon(QIcon(resource_path("resources/icons/signal.png")))
        tool_menu.addAction(self.docsis_action)

        # Separator
        tool_menu.addSeparator()

        # Contacts action
        self.contact_action = QAction("Contacts", self)
        self.contact_action.setToolTip("Contacts")
        self.contact_action.setShortcut("Ctrl+C")
        self.contact_action.setIcon(QIcon(resource_path("resources/icons/contacts.png")))
        tool_menu.addAction(self.contact_action)

        # Tasks action
        self.tasks_action = QAction("Tasks", self)
        self.tasks_action.setToolTip("Tasks")
        self.tasks_action.setShortcut("Ctrl+T")
        self.tasks_action.setIcon(QIcon(resource_path("resources/icons/tasks.png")))
        tool_menu.addAction(self.tasks_action)

        # Projects action
        self.project_action = QAction("Projects", self)
        self.project_action.setToolTip("Projects")
        self.project_action.setShortcut("Ctrl+P")
        self.project_action.setIcon(QIcon(resource_path("resources/icons/projects.png")))
        tool_menu.addAction(self.project_action)

        # Connection mouse hover events for tools menu
        for action in tool_menu.actions():
            action.hovered.connect(lambda act=action: QToolTip.showText(QCursor.pos(), act.toolTip()))


        # Help Menu
        help_menu = self.addMenu("Help")
        help_menu.setObjectName("HelpMenu")
        help_menu.setToolTip("Help")

        # About Scratch Board
        self.about_action = QAction("About")
        self.about_action.setToolTip("About Scratch Board")
        self.about_action.setShortcut("Ctrl+H")
        self.about_action.setIcon(QIcon(resource_path("resources/icons/about.png")))
        help_menu.addAction(self.about_action)

        # Connect hover events for help menu
        self.about_action.hovered.connect(lambda: QToolTip.showText(QCursor.pos(), self.about_action.toolTip()))

    def set_sidebar(self, sidebar):
        self.sidebar = sidebar

        # Wire actions
        self.dash_action.triggered.connect(self.sidebar.dashboard_clicked) # show dashboard
        self.scratch_action.triggered.connect(self.sidebar.open_scratch_pad) # open the scratch notes
        self.bat_action.triggered.connect(self.sidebar.open_bat_file) # run a batch file
        self.modem_action.triggered.connect(self._open_modem_parser)
        self.docsis_action.triggered.connect(self._open_docsis_signal)
        self.contact_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Contacts")) # open contacts view
        self.tasks_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Tasks")) # open tasks view
        self.project_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Projects")) # open projects view
        self.about_action.triggered.connect(lambda: AboutWidget().exec_())

    def _open_modem_parser(self):
        dlg = ModemLogParserView(self.parent())
        dlg.exec()  # modal; blocks main window until closed

    def _open_docsis_signal(self):
        sgnl = SignalReference(self.parent())
        sgnl.exec()