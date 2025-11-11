from PySide6.QtCharts import QChartView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from views.widgets.charts_widget import create_stacked_bar_chart, create_multi_line_chart
from views.widgets.stats_widget import StatsWidget
from views.widgets.mac_widget import MacVendorView
from views.widgets.reference_widget import ReferenceWidget
from views.widgets.time_widget import TimezoneClock
from views.main_view import MainView
from views.contacts_view import ContactsView  # New contacts view
from utils.resource_path import resource_path

class DashboardView(QWidget):
    def __init__(self, model, sidebar, image_path=None):
        super().__init__()
        self.model = model
        self.sidebar = sidebar
        self.image_path = resource_path(image_path) if image_path else None

        self.current_view = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # --- Top layout (banner + stats) ---
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        if image_path:
            self.banner = QLabel(alignment=Qt.AlignCenter)
            top_layout.addWidget(self.banner)
            self.update_banner()

        # Stats widget
        self.stats_widget = StatsWidget(self.model)
        top_layout.addWidget(self.stats_widget)

        # Charts layout
        charts_layout = QHBoxLayout()
        main_layout.addLayout(charts_layout, stretch=3)

        self.stacked_bar_chart = create_stacked_bar_chart(self.model)
        self.stacked_bar_view = QChartView(self.stacked_bar_chart)
        self.stacked_bar_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.stacked_bar_view, stretch=1)

        self.multi_line_chart = create_multi_line_chart(self.model)
        self.multi_line_view = QChartView(self.multi_line_chart)
        self.multi_line_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.multi_line_view, stretch=1)

        # Bottom widgets
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout, stretch=2)

        title_style = "font-weight: bold; font-size: 15px; color: white;"

        def create_section_title(text, icon_name):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            icon_path = resource_path(f"resources/icons/{icon_name}.png")
            label.setText(f'<img src="{icon_path}" width="32" height="32" style="vertical-align: middle; margin-right: 6px">  {text}')
            label.setStyleSheet(title_style)
            return label

        # Reference Section
        self.reference_widget = ReferenceWidget(model)
        ref_layout = QVBoxLayout()
        ref_layout.setAlignment(Qt.AlignTop)  # top alignment
        ref_layout.addWidget(create_section_title("Quick Links/Reference", "reference"))
        ref_layout.addWidget(self.reference_widget)
        # remove ref_layout.addStretch()
        bottom_layout.addLayout(ref_layout, stretch=1)

        # MAC Vendor Section
        self.mac_vendor_view = MacVendorView()
        mac_layout = QVBoxLayout()
        mac_layout.setAlignment(Qt.AlignTop)  # top alignment
        mac_layout.addWidget(create_section_title("MAC Lookup", "robot"))
        mac_layout.addWidget(self.mac_vendor_view)
        # remove mac_layout.addStretch()
        bottom_layout.addLayout(mac_layout, stretch=1)

        # Time Zones Section
        self.timezone_clock = TimezoneClock()
        tz_layout = QVBoxLayout()
        tz_layout.setAlignment(Qt.AlignTop)  # top alignment
        tz_layout.addWidget(create_section_title("Timezones", "watch"))
        tz_layout.addWidget(self.timezone_clock)
        # remove tz_layout.addStretch()
        bottom_layout.addLayout(tz_layout, stretch=1)

        # --- Views ---
        self.notes_view = MainView(self.model.get_all_categories())
        self.contacts_view = ContactsView(self.model.get_all_categories())
        main_layout.addWidget(self.notes_view)
        main_layout.addWidget(self.contacts_view)
        self.contacts_view.hide()
        self.notes_view.add_btn.hide()

        # --- Connect sidebar signals ---
        self.sidebar.category_selected.connect(self.on_category_selected)
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)

        self.load_stylesheet()
        self.refresh_dashboard()

    # View switching
    def on_category_selected(self, category):
        if category == "Contacts":
            self.show_contacts_view()
        elif category == "Notes":
            self.show_notes_view()
        else:
            self.show_dashboard()

    def show_notes_view(self):
        self.notes_view.show()
        self.contacts_view.hide()
        self.stacked_bar_view.show()
        self.multi_line_view.show()
        self.stats_widget.show()

    def show_contacts_view(self):
        self.notes_view.hide()
        self.contacts_view.show()
        self.stacked_bar_view.hide()
        self.multi_line_view.hide()
        self.stats_widget.hide()

    def show_dashboard(self):
        self.notes_view.show()
        self.contacts_view.hide()
        self.stacked_bar_view.show()
        self.multi_line_view.show()
        self.stats_widget.show()

    # Stats
    def update_stats(self, animated=True):
        self.stats_widget.refresh(animated=animated)

    # Charts
    def update_graphs(self):
        self.stacked_bar_chart = create_stacked_bar_chart(self.model)
        self.stacked_bar_view.setChart(self.stacked_bar_chart)

        self.multi_line_chart = create_multi_line_chart(self.model)
        self.multi_line_view.setChart(self.multi_line_chart)

    def refresh_dashboard(self):
        self.update_stats(animated=True)
        self.update_graphs()

    # Banner
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        self.banner.setPixmap(
            pixmap.scaled(200, self.height()//2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    # Stylesheet
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load dark_theme.qss:", e)
