import datetime
import time
import platform
import psutil

from PySide6.QtCore import QTimer, Qt, QObject, Slot, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QProgressBar,
    QFrame, QHBoxLayout, QDialog, QTextEdit, QPushButton
)

from ui.themes.cal_stat_theme import cal_stat_style


# Worker Thread
class ProcessWorker(QObject):
    """
    Worker running in a separate thread to collect system statistics.
    """
    stats_arm = Signal(int, int)
    system_arm = Signal(list)
    net_arm = Signal(str)
    time_arm = Signal(str, str)

    @Slot()
    def get_time(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%a, %b %d, %Y")
        self.time_arm.emit(time_str, date_str)

    @Slot()
    def get_system_info(self):
        try:
            boot = psutil.boot_time()
            uptime = int(time.time() - boot)
            days, rem = divmod(uptime, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, _ = divmod(rem, 60)

            net = psutil.net_io_counters()
            sent = net.bytes_sent / (1024 * 1024)
            recv = net.bytes_recv / (1024 * 1024)

            info = [
                ("Computer", platform.node()),
                ("OS", f"{platform.system()} {platform.release()}"),
                ("Architecture", platform.architecture()[0]),
                ("RAM", f"{round(psutil.virtual_memory().total / (1024 ** 3))} GB"),
                ("Uptime", f"{days}d {hours}h {minutes}m"),
                ("Network:", f"Sent: {sent:.2f} MB | Received: {recv:.2f} MB"),
            ]
        except Exception:
            info = []

        self.system_arm.emit(info)


# Main Widget
class CalStatWidget(QWidget):
    """
    Dashboard widget showing live system statistics.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("Cal + CPU Stats")
        self.setStyleSheet(cal_stat_style)

        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # System Info Box
        sys_frame = QFrame()
        sys_frame.setStyleSheet("background-color: #1E1E1E; border-radius: 8px; padding: 2px;")

        sys_layout = QVBoxLayout(sys_frame)
        sys_layout.setSpacing(4)

        # Time and Date Horizontal Layout
        time_layout = QHBoxLayout()
        time_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Time label
        self.time_label = QLabel()
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Date label
        self.date_label = QLabel()
        self.date_label.setObjectName("date_label")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add labels and layout
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.date_label)
        sys_layout.addLayout(time_layout)

        # System Info Rows
        self.loading_label = QLabel("Loading system information...")
        self.loading_label.setStyleSheet("color: #AAAAAA;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sys_layout.addWidget(self.loading_label)

        self.system_rows = []
        for _ in range(6):
            row = QHBoxLayout()
            label = QLabel("")
            label.setStyleSheet("color: #AAAAAA;")
            value = QLabel("")
            value.setAlignment(Qt.AlignRight)
            value.setStyleSheet("color: #FFFFFF;")

            row.addWidget(label)
            row.addWidget(value)
            self.system_rows.append((label, value))
            sys_layout.addLayout(row)

        layout.addWidget(sys_frame)

        # Thread Setup
        self.thread = QThread(self)
        self.worker = ProcessWorker()
        self.worker.moveToThread(self.thread)

        # Connect workers
        self.worker.system_arm.connect(self.on_system)
        self.worker.time_arm.connect(self.time_update)

        # Spin up the thread
        self.thread.start()

        # Thread Timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.worker.get_time)
        self.clock_timer.start(500)

        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.worker.get_system_info)
        self.sys_timer.start(5000)

    # Thread slots
    @Slot(list)
    def on_system(self, info):
        if info:
            self.loading_label.hide()

        for i, (lbl, val) in enumerate(self.system_rows):
            if i < len(info):
                lbl.setText(info[i][0])
                val.setText(info[i][1])
            else:
                lbl.setText("")
                val.setText("")

    @Slot(str, str)
    def time_update(self, time_str, date_str):
        self.time_label.setText(time_str)
        self.date_label.setText(date_str)

    # Clean close - shut down threads before exiting program
    def closeEvent(self, event):
        self.clock_timer.stop()
        self.sys_timer.stop()
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)
