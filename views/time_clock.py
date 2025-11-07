from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from datetime import datetime
import pytz

class TimezoneClock(QFrame):
    """Displays current time in American timezones with cards and shadows."""

    TIMEZONES = {
        "PT": "US/Pacific",
        "MT": "US/Mountain",
        "CT": "US/Central",
        "ET": "US/Eastern",
        "AKT": "US/Alaska",
        "HST": "US/Hawaii"
    }

    CARD_COLORS = ["#2c3e50", "#34495e", "#16a085", "#27ae60", "#2980b9", "#8e44ad"]

    def __init__(self):
        super().__init__()
        self.setObjectName("TimezoneClock")
        self.setStyleSheet("QFrame#TimezoneClock { background: transparent; }")

        self.labels = {}
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignCenter)

        tz_names = list(self.TIMEZONES.keys())
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        for i, tz_name in enumerate(tz_names):
            # Card frame
            frame = QFrame()
            frame.setObjectName(f"card_{tz_name}")
            frame.setStyleSheet(f"""
                QFrame#{frame.objectName()} {{
                    background-color: {self.CARD_COLORS[i]};
                    border-radius: 12px;
                    padding: 8px 16px;
                }}
                QFrame#{frame.objectName()}:hover {{
                    background-color: {self.CARD_COLORS[i]}AA;
                }}
            """)
            frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            # Drop shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setXOffset(0)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 120))
            frame.setGraphicsEffect(shadow)

            # Label
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: white;")
            lbl.setFont(QFont("Arial", 11, QFont.Bold))
            self.labels[tz_name] = lbl

            # Add label to frame
            frame_layout = QVBoxLayout(frame)
            frame_layout.addWidget(lbl)
            frame_layout.setContentsMargins(0, 0, 0, 0)

            # Add frame to row
            if i < len(tz_names)//2:
                row1.addWidget(frame)
            else:
                row2.addWidget(frame)

        # Add rows to main layout
        row1_widget = QWidget()
        row1_widget.setLayout(row1)
        row2_widget = QWidget()
        row2_widget.setLayout(row2)

        main_layout.addWidget(row1_widget)
        main_layout.addWidget(row2_widget)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_times)
        self.timer.start(1000)
        self.update_times()

    def update_times(self):
        now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
        for name, tz_str in self.TIMEZONES.items():
            tz = pytz.timezone(tz_str)
            local_time = now_utc.astimezone(tz)
            self.labels[name].setText(
                f"{name}\n{local_time.strftime('%H:%M:%S')}\n{local_time.strftime('%a %b %d')}"
            )
