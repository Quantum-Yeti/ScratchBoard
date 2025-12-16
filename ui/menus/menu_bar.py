import os
import traceback

from PySide6.QtGui import QAction, QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QMenuBar, QToolTip, QApplication, QMessageBox, QFileDialog, QMenu

from helpers.modules.sync_helper import sync_db
from models.note_model import NoteModel
from ui.themes.context_menu_theme import menu_style
from utils.resource_path import resource_path
from views.info_widgets.fiber_widget import FiberReferenceDialog
from views.info_widgets.gaming_widget import GamingReference
from views.info_widgets.protocol_widget import InternetProtocolsTimeline
from views.info_widgets.signal_widget import SignalReference
from views.info_widgets.ethernet_widget import EthernetReference
from views.info_widgets.speed_widget import InternetSpeedRequirements
from views.info_widgets.storage_widget import DiskStorageChart
from views.info_widgets.voip_widget import VoIPReference
from views.widgets.calc_widget import SimpleCalcView
from views.widgets.log_widget import ModemLogParserView
from views.notepad_view import NotepadDialog
from views.widgets.about_widget import AboutWidget
from views.info_widgets.wifi_standards_widget import WifiStandardsReference
from views.widgets.mac_pop_widget import MacVendorPopup
from views.widgets.mac_widget import MacVendorView
from views.widgets.md_widget import MarkdownGuideWidget
from views.widgets.password_widget import PassGenWidget
from views.widgets.shortcut_widget import ShortcutGuide

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

class AdjustMenu(QMenu):
    def __init__(self, title, width, parent=None):
        super().__init__(title, parent)
        self._min_width = width

    def showEvent(self, event):
        """Override showEvent to adjust the menu width dynamically."""
        super().showEvent(event)
        self.setMinimumWidth(self._min_width)

class MainMenuBar(QMenuBar):
    """
    Main application menu bar.

    Initializes the menu bar, applies custom styling, defines all action
    placeholders, and constructs the menus.
    """
    def __init__(self, parent=None, model: NoteModel | None = None, dashboard=None):
        super().__init__(parent)

        # Calls the note model to allow import/export
        self.note_model = model

        # Store the dashboard view for _delete_all_notes
        self.dashboard = dashboard

        # File Menu
        self.import_action = None
        self.export_action = None
        self.sync_action = None
        self.exit_action = None

        # Tools Menu
        self.dash_action = None
        self.scratch_action = None
        self.notepad_action = None
        self.bat_action = None
        self.modem_action = None
        self.pwd_action = None
        self.calc_action = None
        self.mac_action = None

        # Views Menu
        self.contact_action = None
        self.internet_action = None
        self.email_action = None
        self.phone_action = None
        self.video_action = None
        self.streaming_action = None
        self.ideas_action = None

        # Charts Menu
        self.signal_action = None
        self.ethernet_action = None
        self.speeds_action = None
        self.fiber_action = None
        self.voip_action = None
        self.gaming_action = None
        self.storage_action = None
        self.protocol_action = None

        # Help Menu
        self.about_action = None
        self.md_action = None
        self.shortcut_action = None

        # Build menus
        self._build_file_menu()
        self._build_views_menu()
        self._build_charts_menu()
        self._build_tools_menu()
        self._build_help_menu()

        # Initialize the sidebar for the categories
        self.sidebar = None

        # Override the dark_theme.qss and apply a hover color to menus via QSS
        self.setStyleSheet(menu_style)

    # Build the File menu
    def _build_file_menu(self):
        file_menu = AdjustMenu("File", 240, self)
        self.addMenu(file_menu)

        self.import_action = QAction("Import Notes", self)
        self.import_action.setShortcut("Alt+I")
        self.import_action.setIcon(QIcon(resource_path("resources/icons/import.png")))
        file_menu.addAction(self.import_action)

        self.export_action = QAction("Export Notes", self)
        self.export_action.setShortcut("Alt+E")
        self.export_action.setIcon(QIcon(resource_path("resources/icons/export.png")))
        file_menu.addAction(self.export_action)

        self.sync_action = QAction("Sync Notes", self)
        self.sync_action.setShortcut("Alt+S")
        self.sync_action.setIcon(QIcon(resource_path("resources/icons/sync.png")))
        file_menu.addAction(self.sync_action)

        file_menu.addSeparator()

        self.delete_db_action = QAction("Delete Database", self)
        self.delete_db_action.setIcon(QIcon(resource_path("resources/icons/delete_db.png")))
        file_menu.addAction(self.delete_db_action)

        file_menu.addSeparator()

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setIcon(QIcon(resource_path("resources/icons/exit.png")))
        file_menu.addAction(self.exit_action)

        self.exit_action.triggered.connect(QApplication.instance().quit)

        # Hover tooltips
        _connect_hover_tooltips(file_menu)

    # Build the View Menu
    def _build_views_menu(self):
        view_menu = AdjustMenu("Views", 200, self)
        self.addMenu(view_menu)

        self.dash_action = QAction("Dashboard", self)
        self.dash_action.setIcon(QIcon(resource_path("resources/icons/dashboard.png")))
        self.dash_action.setShortcut("F1")
        view_menu.addAction(self.dash_action)

        self.contact_action = QAction("Contacts", self)
        self.contact_action.setIcon(QIcon(resource_path("resources/icons/contacts.png")))
        self.contact_action.setShortcut("F2")
        view_menu.addAction(self.contact_action)

        self.copilot_action = QAction("CoPilot", self)
        self.copilot_action.setIcon(QIcon(resource_path("resources/icons/owl.png")))
        self.copilot_action.setShortcut("F3")
        view_menu.addAction(self.copilot_action)

        self.internet_action = QAction("Internet", self)
        self.internet_action.setIcon(QIcon(resource_path("resources/icons/internet.png")))
        self.internet_action.setShortcut("F4")
        view_menu.addAction(self.internet_action)

        self.email_action = QAction("Email", self)
        self.email_action.setIcon(QIcon(resource_path("resources/icons/email.png")))
        self.email_action.setShortcut("F5")
        view_menu.addAction(self.email_action)

        self.phone_action = QAction("Phone", self)
        self.phone_action.setIcon(QIcon(resource_path("resources/icons/phone_white.png")))
        self.phone_action.setShortcut("F6")
        view_menu.addAction(self.phone_action)

        self.video_action = QAction("Video", self)
        self.video_action.setIcon(QIcon(resource_path("resources/icons/video.png")))
        self.video_action.setShortcut("F7")
        view_menu.addAction(self.video_action)

        self.streaming_action = QAction("Streaming", self)
        self.streaming_action.setIcon(QIcon(resource_path("resources/icons/streaming.png")))
        self.streaming_action.setShortcut("F8")
        view_menu.addAction(self.streaming_action)

        self.notes_action = QAction("Notes", self)
        self.notes_action.setIcon(QIcon(resource_path("resources/icons/notes.png")))
        self.notes_action.setShortcut("F9")
        view_menu.addAction(self.notes_action)

        self.ideas_action = QAction("Ideas", self)
        self.ideas_action.setIcon(QIcon(resource_path("resources/icons/ideas.png")))
        self.ideas_action.setShortcut("F10")
        view_menu.addAction(self.ideas_action)

        _connect_hover_tooltips(view_menu)

    def _build_charts_menu(self):
        charts_menu = AdjustMenu("Charts", 260, self)
        self.addMenu(charts_menu)

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

        self.speeds_action = QAction("Bandwidth Req Chart", self)
        self.speeds_action.setIcon(QIcon(resource_path("resources/icons/speed.png")))
        self.speeds_action.setShortcut("Ctrl+S")
        charts_menu.addAction(self.speeds_action)

        self.protocol_action = QAction("Protocol Chart", self)
        self.protocol_action.setIcon(QIcon(resource_path("resources/icons/server.png")))
        self.protocol_action.setShortcut("Alt+R")
        charts_menu.addAction(self.protocol_action)

        self.voip_action = QAction("VoIP Info Chart", self)
        self.voip_action.setIcon(QIcon(resource_path("resources/icons/phone_white.png")))
        self.voip_action.setShortcut("Ctrl+N")
        charts_menu.addAction(self.voip_action)

        self.gaming_action = QAction("Gaming Info Chart", self)
        self.gaming_action.setIcon(QIcon(resource_path("resources/icons/gaming_white.png")))
        self.gaming_action.setShortcut("Ctrl+G")
        charts_menu.addAction(self.gaming_action)

        self.storage_action = QAction("Storage Info Chart", self)
        self.storage_action.setIcon(QIcon(resource_path("resources/icons/storage_white.png")))
        self.storage_action.setShortcut("Alt+D")
        charts_menu.addAction(self.storage_action)

        _connect_hover_tooltips(charts_menu)

    # Build the tools menu
    def _build_tools_menu(self):
        tools_menu = AdjustMenu("Tools", 240, self)
        self.addMenu(tools_menu)

        self.scratch_action = QAction("Scratch Pad", self)
        self.scratch_action.setIcon(QIcon(resource_path("resources/icons/stickynote.png")))
        self.scratch_action.setShortcut("F11")
        tools_menu.addAction(self.scratch_action)

        self.notepad_action = QAction("Notepad", self)
        self.notepad_action.setIcon(QIcon(resource_path("resources/icons/notepad.png")))
        self.notepad_action.setShortcut("F12")
        tools_menu.addAction(self.notepad_action)

        self.bat_action = QAction("Execute Batch File", self)
        self.bat_action.setIcon(QIcon(resource_path("resources/icons/run.png")))
        self.bat_action.setShortcut("Alt+B")
        tools_menu.addAction(self.bat_action)

        self.modem_action = QAction("Log Parser", self)
        self.modem_action.setIcon(QIcon(resource_path("resources/icons/network.png")))
        self.modem_action.setShortcut("Alt+L")
        tools_menu.addAction(self.modem_action)

        self.pwd_action = QAction("Password Generator", self)
        self.pwd_action.setIcon(QIcon(resource_path("resources/icons/pw.png")))
        self.pwd_action.setShortcut("Alt+P")
        tools_menu.addAction(self.pwd_action)

        self.calc_action = QAction("Calculator", self)
        self.calc_action.setIcon(QIcon(resource_path("resources/icons/calculator.png")))
        self.calc_action.setShortcut("Alt+C")
        tools_menu.addAction(self.calc_action)

        self.mac_action = QAction("MAC Vendor Query", self)
        self.mac_action.setIcon(QIcon(resource_path("resources/icons/robot_white.png")))
        self.mac_action.setShortcut("Alt+T")
        tools_menu.addAction(self.mac_action)

        _connect_hover_tooltips(tools_menu)

    # Build the Help menu
    def _build_help_menu(self):
        help_menu = AdjustMenu("Help", 260, self)
        self.addMenu(help_menu)

        self.shortcut_action = QAction("Keyboard Shortcuts", self)
        self.shortcut_action.setIcon(QIcon(resource_path("resources/icons/keyboard_alt_white.png")))
        self.shortcut_action.setShortcut("Alt+K")
        help_menu.addAction(self.shortcut_action)

        self.md_action = QAction("MarkDown Guide", self)
        self.md_action.setIcon(QIcon(resource_path("resources/icons/markdown.png")))
        self.md_action.setShortcut("Alt+M")
        help_menu.addAction(self.md_action)

        self.about_action = QAction("About Scratch Board", self)
        self.about_action.setIcon(QIcon(resource_path("resources/icons/about.png")))
        self.about_action.setShortcut("Alt+A")
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

        # Wire the file menu
        self.import_action.triggered.connect(self._import_notes)
        self.export_action.triggered.connect(self._export_notes)
        self.sync_action.triggered.connect(self._sync_db)
        self.delete_db_action.triggered.connect(self._delete_database)

        # Wire the charts
        self.signal_action.triggered.connect(self._open_signal_chart)
        self.ethernet_action.triggered.connect(self._open_ethernet_chart)
        self.wifi_standards_action.triggered.connect(self._open_wifi_chart)
        self.speeds_action.triggered.connect(self._open_speed_chart)
        self.fiber_action.triggered.connect(self._open_fiber_chart)
        self.protocol_action.triggered.connect(self._open_protocol_chart)
        self.voip_action.triggered.connect(self._open_voip_chart)
        self.gaming_action.triggered.connect(self._open_gaming_chart)
        self.storage_action.triggered.connect(self._open_storage_chart)

        # Wire the view categories
        self.contact_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Contacts"))
        self.copilot_action.triggered.connect(lambda: self.sidebar.category_selected.emit("CoPilot"))
        self.internet_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Internet"))
        self.email_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Email"))
        self.phone_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Phone"))
        self.video_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Video"))
        self.streaming_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Streaming"))
        self.notes_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Notes"))
        self.ideas_action.triggered.connect(lambda: self.sidebar.category_selected.emit("Ideas"))

        # Wire the tools
        self.scratch_action.triggered.connect(self.sidebar.open_scratch_pad)  # open the scratch notes
        self.notepad_action.triggered.connect(self._open_notepad)
        self.bat_action.triggered.connect(self.sidebar.open_bat_file)  # run a batch file
        self.modem_action.triggered.connect(self._open_modem_parser)
        self.pwd_action.triggered.connect(self._open_pw_gen)
        self.calc_action.triggered.connect(self._open_calc)
        self.mac_action.triggered.connect(self._open_mac)

        # Wire the help menu
        self.shortcut_action.triggered.connect(self._open_shortcuts)
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

    def _open_protocol_chart(self):
        prot = InternetProtocolsTimeline(self.parent())
        prot.exec()

    def _open_voip_chart(self):
        voip = VoIPReference(self.parent())
        voip.exec()

    def _open_gaming_chart(self):
        gaming = GamingReference(self.parent())
        gaming.exec()

    def _open_storage_chart(self):
        storage = DiskStorageChart(self.parent())
        storage.exec()

    def _open_shortcuts(self):
        short = ShortcutGuide(self.parent())
        short.exec()

    def _open_md_guide(self):
        if not hasattr(self, '_md_widget'):
            self._md_widget = MarkdownGuideWidget()
        self._md_widget.show()

    def _open_pw_gen(self):
        pwgen = PassGenWidget(self.parent())
        pwgen.exec()

    def _open_calc(self):
        calc = SimpleCalcView(self.parent())
        calc.exec()

    def _open_mac(self):
        mac = MacVendorPopup(self.parent())
        mac.show()

    def _export_notes(self):
        if not self.note_model:
            QMessageBox.warning(self, "Error", "Database export failed..")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Notes to ZIP", "", "ZIP Files (*.zip)"
        )
        if path:
            try:
                self.note_model.export_to_zip(path)
                QMessageBox.information(self, "Success", f"Notes exported to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{e}")

    def _import_notes(self):
        if not self.note_model:
            QMessageBox.warning(self, "Error", "Note model is not initialized.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Import Notes from ZIP", "", "ZIP Files (*.zip)"
        )
        if path:
            try:
                self.note_model.import_from_zip(path)
                QMessageBox.information(self, "Success", f"Notes imported from {path}")

                # OK button triggers dashboard view
                self.sidebar.dashboard_clicked.emit()  # Emits the signal to trigger dashboard view

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Import failed:\n{e}")

    def _delete_database(self):
        if not self.note_model:
            QMessageBox.warning(self, "Error", "We're sorry - something went wrong.")
            return

        # Loads a skull icon
        skull_icon = QPixmap(resource_path("resources/icons/skull.png"))
        skull_icon = skull_icon.scaled(72, 72)

        # Danger Popup with icon
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Scratch Board: Delete Database")
        confirm.setText(
            "This action will permanently delete the entire database.\n"
        )
        confirm.setIconPixmap(skull_icon)
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm.setDefaultButton(QMessageBox.StandardButton.No)
        confirm.setDetailedText("This action is permanent. Please back up your database before continuing.")
        confirm.setEscapeButton(QMessageBox.StandardButton.No)  # ESC cancels

        response = confirm.exec()

        if response == QMessageBox.StandardButton.Yes:
            try:
                self.note_model.delete_all_notes()
                QMessageBox.information(self, "Scratch Board: Database Deleted", "All data has been deleted.")

                # Forces refresh
                if self.dashboard:
                    self.dashboard.go_to_dashboard()
                    self.dashboard.refresh_dashboard()  # refresh dashboard

                # Directly refresh the ReferenceWidget without waiting for dashboard button click
                if self.dashboard and hasattr(self.dashboard, 'reference_widget'):
                    self.dashboard.reference_widget.refresh_references()  # Refresh reference widget immediately

                # Trigger calendar update
                if hasattr(self.dashboard, 'calendar_widget'):
                    self.dashboard.calendar_widget.refresh_calendar()

            except Exception as e:
                error_message = f"Failed to delete notes:\n{e}\n\nStack Trace:\n{traceback.format_exc()}"
                QMessageBox.critical(self, "Error", error_message)

    def _sync_db(self):
        # Dialog window to select zipped database export
        db_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database (Export to ZIP first)", "", "Zipped Files (*.zip)"
        )
        if not db_path:
            return

        # Default OneDrive folder
        default_onedrive = os.path.join(os.path.expanduser("~"), "OneDrive", "Scratch Board")

        # Calls sync_helper.py
        sync_db(db_path, default_onedrive)

        # Notify user on success
        QMessageBox.information(self, "Success", f"Database synced to OneDrive:\n{default_onedrive}")
