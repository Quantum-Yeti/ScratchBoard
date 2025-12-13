import datetime
import calendar
import psutil

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QProgressBar, QFrame, QGridLayout, QHBoxLayout
)

from ui.themes.cal_stat_theme import cal_stat_style


class CalStatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Cal + CPU Stats")
        self.setStyleSheet(cal_stat_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Time Label
        self.time_label = QLabel(self)
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(0, -5, 0, 0)
        layout.addWidget(self.time_label)

        # Date Label
        self.date_label = QLabel(self)
        self.date_label.setObjectName("date_label")
        self.date_label.setStyleSheet("font-weight: bold;")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        # CPU + RAM Section
        stats_frame = QFrame(self)
        stats_frame.setFrameShape(QFrame.NoFrame)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(6)

        # Horizontal layout for bars
        bars_layout = QHBoxLayout()
        bars_layout.setSpacing(10)
        bars_layout.setContentsMargins(0, 0, 0, 0)

        # CPU Bar
        cpu_frame = QVBoxLayout()
        cpu_label = QLabel("CPU", self)
        cpu_label.setStyleSheet("font-weight: bold; color: #B8F1B0;")
        cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_bar = QProgressBar(self)
        self.cpu_bar.setFormat("%p%")
        cpu_frame.addWidget(cpu_label)
        cpu_frame.addWidget(self.cpu_bar)
        bars_layout.addLayout(cpu_frame)

        # RAM Bar
        ram_frame = QVBoxLayout()
        ram_label = QLabel("RAM", self)
        ram_label.setStyleSheet("font-weight: bold; color: #B8F1B0;")
        ram_label.setAlignment(Qt.AlignCenter)
        self.ram_bar = QProgressBar(self)
        self.ram_bar.setFormat("%p%")
        ram_frame.addWidget(ram_label)
        ram_frame.addWidget(self.ram_bar)
        bars_layout.addLayout(ram_frame)

        # Add bars layout to main stats layout
        stats_layout.addLayout(bars_layout)

        # Add stats_frame to main layout
        layout.addWidget(stats_frame)

        # Process box
        process_frame = QFrame(self)
        process_layout = QVBoxLayout(process_frame)
        process_layout.setSpacing(0)
        process_layout.setContentsMargins(0, 0, 0, 0)

        self.process_header = QLabel(process_frame)
        self.process_header.setObjectName("process_header")
        self.process_header.setAlignment(Qt.AlignCenter)
        self.process_header.setContentsMargins(0, 0, 0, 0)
        process_layout.addWidget(self.process_header)

        self.process_labels = []
        self.process_rows = []

        for _ in range(5):
            row = QFrame(process_frame)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)

            name_lbl = QLabel("-", row)
            name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            cpu_lbl = QLabel("-", row)
            cpu_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_layout.addWidget(name_lbl, 1)
            row_layout.addWidget(cpu_lbl, 0)

            self.process_rows.append((name_lbl, cpu_lbl))
            process_layout.addWidget(row)

        layout.addWidget(process_frame)

        # Initial updates
        self.update_time()
        self.update_stats()
        self.update_processes()

        # Timers
        self.timer_processes = QTimer(self)
        self.timer_processes.timeout.connect(self.update_processes)
        self.timer_processes.start(6000)

        self.timer_clock = QTimer(self)
        self.timer_clock.timeout.connect(self.update_time_and_stats)
        self.timer_clock.start(1000)

    # Update Functions
    def update_all(self):
        self.update_time()
        self.update_stats()

    def update_time_and_stats(self):
        self.update_time()
        self.update_stats()

    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
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

    def update_processes(self):
        processes = []

        for proc in psutil.process_iter(attrs=["name", "cpu_percent"]):
            try:
                cpu = proc.info["cpu_percent"]
                if cpu is None:
                    continue
                if proc.info["name"] and "idle" in proc.info["name"].lower():
                    continue
                processes.append((proc.info["name"], cpu))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x[1], reverse=True)
        top = processes[:5]

        for i, row in enumerate(self.process_rows):
            name_lbl, cpu_lbl = row
            if i < len(top):
                name, cpu = top[i]
                name_lbl.setText(name)
                cpu_lbl.setText(f"{cpu:.1f}%")
            else:
                name_lbl.setText("-")
                cpu_lbl.setText("")
