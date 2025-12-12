from PySide6.QtCharts import QChartView, QChart
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from views.widgets.charts_widget import create_stacked_bar_chart, create_multi_line_chart
from views.widgets.stats_widget import StatsWidget
from views.widgets.mac_widget import MacVendorView
from views.widgets.reference_widget import ReferenceWidget
from views.widgets.cal_widget import CalendarDashboardWidget
from views.notes.main_note_view import MainView
from views.contacts_view import ContactsView
from utils.resource_path import resource_path

class DashboardView(QWidget):
    def __init__(self, model, sidebar, image_path=None):
        super().__init__()
        self.model = model
        self.sidebar = sidebar
        self.image_path = resource_path(image_path) if image_path else None
        self.current_view = None  # Tracks current active view

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 0)
        main_layout.setSpacing(12)

        # Sidebar connections
        self.sidebar.category_selected.connect(self.on_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        # Dashboard Content
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Top: Banner + Stats
        top_layout = QHBoxLayout()
        content_layout.addLayout(top_layout)

        if image_path:
            self.banner = QLabel(alignment=Qt.AlignCenter)
            top_layout.addWidget(self.banner)
            self.update_banner()

        self.stats_widget = StatsWidget(self.model)
        top_layout.addWidget(self.stats_widget)

        # Charts
        charts_layout = QHBoxLayout()
        content_layout.addLayout(charts_layout, stretch=3)

        self.stacked_bar_chart = create_stacked_bar_chart(self.model)
        self.stacked_bar_view = QChartView(self.stacked_bar_chart)
        self.stacked_bar_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.stacked_bar_view, stretch=1)

        self.multi_line_chart = create_multi_line_chart(self.model)
        self.multi_line_view = QChartView(self.multi_line_chart)
        self.multi_line_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.multi_line_view, stretch=1)

        self.stacked_bar_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.multi_line_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Bottom Widgets
        bottom_layout = QHBoxLayout()
        #bottom_layout.addStretch()

        # Helper for section titles
        def create_section_title(text, icon_name, icon_size=32):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignHCenter)

            icon_label = QLabel()
            pixmap = QPixmap(resource_path(f"resources/icons/{icon_name}.png"))
            pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setContentsMargins(0, 12, 0, 0)

            text_label = QLabel(text)
            text_label.setFixedHeight(icon_size)
            text_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white; margin-top: 10px; font-family: Segoe UI;")

            layout.addWidget(icon_label)
            layout.addWidget(text_label)

            return container

        # Reference Section
        self.reference_widget = ReferenceWidget(model)
        ref_layout = QVBoxLayout()
        self.reference_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ref_layout.setAlignment(Qt.AlignTop)
        ref_layout.addWidget(create_section_title("Quick Links/Reference", "reference"))
        ref_layout.addWidget(self.reference_widget)
        bottom_layout.addLayout(ref_layout, stretch=1)

        # MAC Vendor Section
        self.mac_vendor_view = MacVendorView()
        self.mac_vendor_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mac_layout = QVBoxLayout()
        mac_layout.setAlignment(Qt.AlignTop)
        mac_layout.addWidget(create_section_title("MAC Lookup", "robot"))
        mac_layout.addWidget(self.mac_vendor_view)
        bottom_layout.addLayout(mac_layout, stretch=1)

        # Calendar Widget Section
        self.cal_widget = CalendarDashboardWidget()
        self.cal_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cal_layout = QVBoxLayout()
        cal_layout.setAlignment(Qt.AlignTop)
        cal_layout.addWidget(create_section_title("Calendar", "calendar"))
        cal_layout.addWidget(self.cal_widget)
        bottom_layout.addLayout(cal_layout, stretch=1)

        # Bottom spacing
        bottom_spacing = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        content_layout.addLayout(bottom_layout)
        content_layout.addItem(bottom_spacing)

        # View Container (dynamic view switching)
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(0)
        main_layout.addWidget(self.view_container)

        # Pre-create Notes & Contacts views
        self.notes_view = MainView(self.model.get_all_categories())
        self.notes_view.add_btn.hide()
        self.contacts_view = ContactsView(self.model.get_all_categories())

        # Show dashboard by default
        self.set_current_view(self.content_widget)

        self.load_stylesheet()
        self.refresh_dashboard()

    # View Switching
    def set_current_view(self, view: QWidget):
        """Removes old view and adds new one to container"""
        if self.current_view:
            self.view_layout.removeWidget(self.current_view)
            self.current_view.setParent(None)
        self.current_view = view
        if self.current_view:
            self.view_layout.addWidget(self.current_view)

    def on_category_selected(self, category):
        if category == "Contacts":
            self.set_current_view(self.contacts_view)
        elif category == "Notes":
            self.set_current_view(self.notes_view)
        else:
            self.set_current_view(self.content_widget)

    def show_dashboard(self):
        self.set_current_view(self.content_widget)

    # Stats / Graphs
    def update_stats(self, animated=True):
        self.stats_widget.refresh(animated=animated)

    def update_graphs(self):
        """
        Refreshes both stacked bar and multi-line charts.
        Old charts are removed, new charts are created, and legends update automatically.
        """
        # --- Remove old series from stacked bar chart ---
        if self.stacked_bar_view.chart():
            self.stacked_bar_view.chart().removeAllSeries()

        # --- Remove old series from multi-line chart ---
        if self.multi_line_view.chart():
            self.multi_line_view.chart().removeAllSeries()

        # --- Create new charts ---
        self.stacked_bar_chart = create_stacked_bar_chart(self.model)
        self.multi_line_chart = create_multi_line_chart(self.model)

        # --- Replace charts in QChartView ---
        self.stacked_bar_view.setChart(self.stacked_bar_chart)
        self.multi_line_view.setChart(self.multi_line_chart)

        # --- Force redraw to ensure view updates ---
        self.stacked_bar_view.repaint()
        self.multi_line_view.repaint()

    def refresh_dashboard(self):
        self.reference_widget.refresh_references()
        self.update_stats(animated=True)
        self.update_graphs()

    # Banner image
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        self.banner.setPixmap(
            pixmap.scaled(200, self.height()//2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def go_to_dashboard(self):
        """Helper method to switch to the dashboard view and refresh it."""
        self.set_current_view(self.content_widget)  # Switch to dashboard view (content_widget in this case)
        self.refresh_dashboard()  # Refresh the dashboard stats and graphs

    # Stylesheet
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load main_theme.qss:", e)
