import datetime
import calendar
import psutil

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QProgressBar, QFrame, QGridLayout
)

from ui.themes.cal_widget_theme import cal_style


class CalendarDashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Calendar")
        self.setStyleSheet(cal_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Time Label
        self.time_label = QLabel()
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(0, -5, 0, 0)
        layout.addWidget(self.time_label)

        # Date Label
        self.date_label = QLabel()
        self.date_label.setObjectName("date_label")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        # CPU + RAM Section
        stats_box = QVBoxLayout()
        stats_box.setSpacing(6)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFormat("CPU Usage: %p%")
        stats_box.addWidget(self.cpu_bar)

        self.ram_bar = QProgressBar()
        self.ram_bar.setFormat("Memory Usage: %p%")
        stats_box.addWidget(self.ram_bar)

        layout.addLayout(stats_box)

        # Calendar box
        calendar_frame = QFrame()
        cal_layout = QVBoxLayout(calendar_frame)
        cal_layout.setSpacing(4)

        self.calendar_header = QLabel("", alignment=Qt.AlignCenter)
        self.calendar_header.setObjectName("calendar_header")
        cal_layout.addWidget(self.calendar_header)

        self.calendar_grid = QGridLayout()
        self.calendar_grid.setHorizontalSpacing(6)
        self.calendar_grid.setVerticalSpacing(4)
        cal_layout.addLayout(self.calendar_grid)

        layout.addWidget(calendar_frame)

        # Update time + stats every second
        self.update_time()
        self.update_stats()
        self.update_calendar()  # initial build

        self.timer_clock = QTimer(self)
        self.timer_clock.timeout.connect(self.update_time_and_stats)
        self.timer_clock.start(1000)

        # Update calendar once per day at midnight
        self.timer_calendar = QTimer(self)
        self.timer_calendar.timeout.connect(self.update_calendar)
        self.timer_calendar.start(60 * 60 * 1000)

    #   Update Functions
    def update_all(self):
        self.update_time()
        self.update_stats()
        self.update_calendar()

    def update_time_and_stats(self):
        self.update_time()
        self.update_stats()

    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))

    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
        except Exception:
            cpu = 0
            mem = 0

        self.cpu_bar.setValue(cpu)
        self.ram_bar.setValue(mem)

    def update_calendar(self):
        today = datetime.date.today()
        year, month = today.year, today.month

        self.calendar_header.setText(f"{calendar.month_name[month]} {year}")

        # Clear old labels
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Weekday headers
        for i, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold;")
            self.calendar_grid.addWidget(lbl, 0, i)

        # Days
        month_cal = calendar.Calendar().monthdayscalendar(year, month)
        for row, week in enumerate(month_cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                lbl = QLabel(str(day))
                lbl.setAlignment(Qt.AlignCenter)

                # Highlight today
                if day == today.day:
                    lbl.setStyleSheet(
                        "background: #4A90E2; color: white; border-radius: 4px;"
                    )

                self.calendar_grid.addWidget(lbl, row, col)
