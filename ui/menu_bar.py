from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QMenuBar, QToolTip, QApplication

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
        file_menu.addAction(self.import_action)

        # TODO: implement export of SQLite db
        # Export database action
        self.export_action = QAction("Export Notes", self)
        self.export_action.setToolTip("Export Database")
        self.export_action.setShortcut("Ctrl+E")
        file_menu.addAction(self.export_action)

        # Exit action
        self.exit_action = QAction("Exit", self)
        self.exit_action.setToolTip("Exit application")
        self.exit_action.setShortcut("Ctrl+Q")
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
        tool_menu.addAction(self.dash_action)

        # Scratch notes action
        self.scratch_action = QAction("Scratch Board", self)
        self.scratch_action.setToolTip("Scratch Board")
        self.scratch_action.setShortcut("Ctrl+B")
        tool_menu.addAction(self.scratch_action)

        # Run a batch file action
        self.bat_action = QAction("Run *.bat", self)
        self.bat_action.setToolTip("Run *.bat")
        self.bat_action.setShortcut("Ctrl+R")
        tool_menu.addAction(self.bat_action)

        # Separator
        tool_menu.addSeparator()

        # Contacts action
        self.contact_action = QAction("Contacts", self)
        self.contact_action.setToolTip("Contacts")
        self.contact_action.setShortcut("Ctrl+C")
        tool_menu.addAction(self.contact_action)

        # Tasks action
        self.tasks_action = QAction("Tasks", self)
        self.tasks_action.setToolTip("Tasks")
        self.tasks_action.setShortcut("Ctrl+T")
        tool_menu.addAction(self.tasks_action)

        # Projects action
        self.project_action = QAction("Projects", self)
        self.project_action.setToolTip("Projects")
        self.project_action.setShortcut("Ctrl+P")
        tool_menu.addAction(self.project_action)

        # Connection mouse hover events for tools menu
        for action in tool_menu.actions():
            action.hovered.connect(lambda act=action: QToolTip.showText(QCursor.pos(), act.toolTip()))


        # Help Menu
        help_menu = self.addMenu("Help")
        help_menu.setObjectName("HelpMenu")
        self.about_action = QAction("About", self)
        self.about_action.setToolTip("About this application")
        help_menu.addAction(self.about_action)

        # Connect hover events for help menu
        self.about_action.hovered.connect(lambda: QToolTip.showText(QCursor.pos(), self.about_action.toolTip()))

    def set_sidebar(self, sidebar):
        self.sidebar = sidebar

        # Wire actions
        self.dash_action.triggered.connect(self.sidebar.dashboard_clicked) # show dashboard
        self.scratch_action.triggered.connect(self.sidebar.open_scratch_pad) # open the scratch notes
        self.bat_action.triggered.connect(self.sidebar.open_bat_file) # run a batch file
        self.contact_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Contacts")) # open contacts view
        self.tasks_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Tasks")) # open tasks view
        self.project_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Projects")) # open projects view
        self.about_action.triggered.connect(lambda: AboutWidget().exec_())