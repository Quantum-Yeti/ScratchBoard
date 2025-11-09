from PySide6.QtCharts import QChartView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from views.widgets.charts_widget import create_stacked_bar_chart, create_multi_line_chart
from views.widgets.stats_widget import StatsWidget
from views.widgets.mac_widget import MacVendorView
from views.widgets.reference_widget import ReferenceWidget
from views.widgets.time_widget import TimezoneClock
from utils.resource_path import resource_path

class DashboardView(QWidget):
    def __init__(self, model, image_path=None):
        super().__init__()
        self.model = model
        self.image_path = resource_path(image_path) if image_path else None

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

        # --- Charts ---
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

        # --- Bottom widgets ---
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout, stretch=2)

        self.reference_widget = ReferenceWidget()
        bottom_layout.addWidget(self.reference_widget, stretch=2)
        self.mac_vendor_view = MacVendorView()
        bottom_layout.addWidget(self.mac_vendor_view, stretch=1)
        tz_layout = QVBoxLayout()
        tz_title = QLabel("Timezones")
        tz_title.setAlignment(Qt.AlignCenter)
        tz_layout.addWidget(tz_title)
        self.timezone_clock = TimezoneClock()
        tz_layout.addWidget(self.timezone_clock)
        bottom_layout.addLayout(tz_layout, stretch=1)

        self.load_stylesheet()
        self.refresh_dashboard()

    # --- Stats ---
    def update_stats(self, animated=True):
        self.stats_widget.refresh(animated=animated)

    # --- Charts ---
    def update_graphs(self):
        self.stacked_bar_chart = create_stacked_bar_chart(self.model)
        self.stacked_bar_view.setChart(self.stacked_bar_chart)

        self.multi_line_chart = create_multi_line_chart(self.model)
        self.multi_line_view.setChart(self.multi_line_chart)

    # --- Dashboard ---
    def refresh_dashboard(self):
        self.update_stats(animated=True)
        self.update_graphs()

    # --- Banner ---
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        self.banner.setPixmap(
            pixmap.scaled(200, self.height()//2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load dark_theme.qss:", e)
