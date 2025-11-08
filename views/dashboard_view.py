
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap, QPainter, QColor

from PySide6.QtCharts import (
    QChart, QChartView,
    QLineSeries,
    QBarSet, QBarSeries,
    QValueAxis, QCategoryAxis, QBoxPlotSeries, QBoxSet, QScatterSeries
)

from utils.resource_path import resource_path
from helpers.dashboard_stats import calculate_stats
from views.recent_note_view import RecentNoteView
from views.reference_view import ReferenceWidget
from views.time_clock import TimezoneClock


class StatCard(QFrame):
    """A dark stat card with animated numeric value."""
    def __init__(self, title, value="0"):
        super().__init__()
        self._value = 0
        self._display_value = QLabel(value, alignment=Qt.AlignCenter)
        self.setObjectName("StatCard")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title, alignment=Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #fff;")
        self._display_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #4c8caf;")

        layout.addWidget(title_label)
        layout.addWidget(self._display_value)

    # Property for animation
    def _set_value(self, val):
        self._value = val
        self._display_value.setText(str(int(val)))

    def _get_value(self):
        return self._value

    value = Property(float, _get_value, _set_value)


class DashboardView(QWidget):
    def __init__(self, model, image_path=None):
        super().__init__()
        self.model = model
        self.image_path = resource_path(image_path) if image_path else None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # --- Banner + Stats ---
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        if image_path:
            self.banner = QLabel(alignment=Qt.AlignCenter)
            self.banner.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            top_layout.addWidget(self.banner)
            self.update_banner()

        stats_layout = QHBoxLayout()
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout.addWidget(stats_widget)

        self.cards = {
            "total": StatCard("Total Notes"),
            "cats": StatCard("Categories"),
            "monthly": StatCard("Notes This Month"),
        }
        for c in self.cards.values():
            stats_layout.addWidget(c)

        # --- Charts using QtCharts ---
        charts_layout = QHBoxLayout()
        main_layout.addLayout(charts_layout, stretch=3)

        # Line Chart
        self.line_chart = QChart()
        self.line_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.line_chart.setBackgroundVisible(False)

        self.line_view = QChartView(self.line_chart)
        self.line_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.line_view)

        # Heat Grid Bar Chart
        self.heat_chart = QChart()
        self.heat_chart.setAnimationOptions(QChart.AllAnimations)
        self.heat_chart.setBackgroundVisible(False)

        self.heat_view = QChartView(self.heat_chart)
        self.heat_view.setRenderHint(QPainter.Antialiasing)
        charts_layout.addWidget(self.heat_view)

        # --- Recent + Clock ---
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout, stretch=2)

        self.reference_widget = ReferenceWidget()
        bottom_layout.addWidget(self.reference_widget, stretch=3)


        tz_layout = QVBoxLayout()
        tz_title = QLabel("Timezones")
        tz_title.setAlignment(Qt.AlignCenter)
        tz_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: white;")
        tz_layout.addWidget(tz_title)

        self.timezone_clock = TimezoneClock()
        tz_layout.addWidget(self.timezone_clock)

        tz_widget = QWidget()
        tz_widget.setLayout(tz_layout)
        bottom_layout.addWidget(tz_widget)

        # Apply stylesheet immediately
        self.load_stylesheet()

        # Initial data
        self.refresh_dashboard()

    # --- Stats ---
    def update_stats(self, animated=True):
        values = calculate_stats(self.model)
        for key, val in values.items():
            card = self.cards[key]
            if animated:
                anim = QPropertyAnimation(card, b"value", self)
                anim.setDuration(700)
                anim.setStartValue(card.value)
                anim.setEndValue(val)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.start()
                card._anim = anim
            else:
                card._set_value(val)

    # --- Graphs ---
    def update_graphs(self):
        self.update_line_chart()
        self.update_scatter()

    def refresh_dashboard(self):
        self.update_stats(animated=True)
        self.update_graphs()

    # Line Chart
    def update_line_chart(self):
        self.line_chart.removeAllSeries()
        self.line_chart.removeAxis(self.line_chart.axisX())
        self.line_chart.removeAxis(self.line_chart.axisY())

        categories = self.model.get_all_categories()
        all_dates = sorted({datetime.fromisoformat(n["created"]).date()
                            for c in categories
                            for n in self.model.get_notes(category_name=c)})
        if not all_dates:
            return

        x_vals = list(range(len(all_dates)))

        for cat in categories:
            notes = self.model.get_notes(category_name=cat)
            y_vals = []
            cumulative = 0

            for d in all_dates:
                daily = sum(1 for n in notes if datetime.fromisoformat(n["created"]).date() == d)
                cumulative += daily
                y_vals.append(cumulative)

            series = QLineSeries()
            for i, y in zip(x_vals, y_vals):
                series.append(i, y)

            series.setName(cat)
            self.line_chart.addSeries(series)

        # Axes
        axis_x = QCategoryAxis()
        axis_y = QValueAxis()

        # X-axis labels
        for i, d in enumerate(all_dates):
            axis_x.append(d.strftime("%b %d"), i)

        axis_x.setLabelsColor(QColor("white"))
        axis_x.setLinePenColor(QColor(0, 0, 0, 0))
        axis_x.setGridLineVisible(False)


        # Y-axis
        axis_y.setTitleText("Total Notes")
        axis_y.setLabelsColor(QColor("white"))
        axis_y.setLinePenColor(QColor(0, 0, 0, 0))
        axis_y.setGridLineVisible(False)

        # Add axes and attach
        self.line_chart.addAxis(axis_x, Qt.AlignBottom)
        self.line_chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.line_chart.series():
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        # Legend color
        legend = self.line_chart.legend()
        legend.setVisible(True)
        legend.setLabelColor(QColor("white"))

        self.line_chart.setTitle("Cumulative Notes by Category")
        self.line_chart.setTitleBrush(QColor("white"))

    def update_scatter(self):
        """Scatter plot of note lengths per category."""
        self.heat_chart.removeAllSeries()
        categories = self.model.get_all_categories()
        if not categories:
            return

        for cat in categories:
            notes = self.model.get_notes(category_name=cat)
            if not notes:
                continue

            series = QScatterSeries()
            series.setName(cat)
            series.setMarkerSize(10)
            series.setColor(QColor(64, 181, 246))  # light blue per category
            # Optionally pick different colors per category
            series.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))

            for idx, note in enumerate(notes):
                # X-axis: index of the note for this category
                # Y-axis: length of the note
                series.append(idx, len(note["content"]))

            self.heat_chart.addSeries(series)

        # X-axis: just note index
        axis_x = QValueAxis()
        axis_x.setTitleText("Note Index")
        axis_x.setLabelsColor(QColor("white"))
        axis_x.setLinePenColor(QColor(0, 0, 0, 0))
        axis_x.setGridLineVisible(False)
        self.heat_chart.addAxis(axis_x, Qt.AlignBottom)

        # Y-axis: note length
        axis_y = QValueAxis()
        axis_y.setTitleText("Note Length")
        axis_y.setLabelsColor(QColor("white"))
        axis_y.setLinePenColor(QColor(0, 0, 0, 0))
        axis_y.setGridLineVisible(False)
        self.heat_chart.addAxis(axis_y, Qt.AlignLeft)

        # Attach axes to all series
        for series in self.heat_chart.series():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        # Legend
        legend = self.heat_chart.legend()
        legend.setVisible(True)
        legend.setLabelColor(QColor("white"))

        # Chart title
        self.heat_chart.setTitle("Scatter Plot: Note Length per Category")
        self.heat_chart.setTitleBrush(QColor("white"))

    # --- Banner ---
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        max_width = 200
        max_height = self.height() // 2
        self.banner.setPixmap(
            pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "banner"):
            self.update_banner()

    def open_note_callback(self, note):
        self.parent().open_editor(note["id"])

    # --- Stylesheet ---
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load dark_theme.qss:", e)
