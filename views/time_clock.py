from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QWidget
from PySide6.QtCore import Qt, QTimer
from datetime import datetime
import pytz

class TimezoneClock(QFrame):
    """Displays current time in major American timezones in two rows."""

    TIMEZONES = {
        "PT": "US/Pacific",
        "MT": "US/Mountain",
        "CT": "US/Central",
        "ET": "US/Eastern",
        "AKT": "US/Alaska",
        "HST": "US/Hawaii"
    }

    def __init__(self):
        super().__init__()
        self.setObjectName("TimezoneClock")
        self.setStyleSheet("""
            QFrame#TimezoneClock {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                color: #dddddd;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        self.labels = {}
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setAlignment(Qt.AlignCenter)

        # Split timezones into two rows
        tz_names = list(self.TIMEZONES.keys())
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        for i, tz_name in enumerate(tz_names):
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # <-- expand horizontally
            self.labels[tz_name] = lbl
            if i < len(tz_names)//2:
                row1.addWidget(lbl)
            else:
                row2.addWidget(lbl)

        row1_widget = QWidget()
        row1_widget.setLayout(row1)
        row2_widget = QWidget()
        row2_widget.setLayout(row2)

        main_layout.addWidget(row1_widget)
        main_layout.addWidget(row2_widget)

        # Allow the whole widget to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Timer to update every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_times)
        self.timer.start(1000)
        self.update_times()

    def update_times(self):
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        for name, tz_str in self.TIMEZONES.items():
            tz = pytz.timezone(tz_str)
            local_time = now_utc.astimezone(tz)
            self.labels[name].setText(f"{name}: {local_time.strftime('%H:%M:%S')}")
