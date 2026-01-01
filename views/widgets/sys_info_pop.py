import datetime
import sys
import time
import platform
import psutil

from PySide6.QtCore import QTimer, Qt, QObject, Slot, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
)

from utils.custom_context_menu import ContextMenuUtility


class StatsWorker(QObject):
    system_signal = Signal(list)
    time_signal = Signal(str, str)
    user_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.session_start = time.time()

    @Slot()
    def update_time(self):
        now = datetime.datetime.now()
        self.time_signal.emit(
            now.strftime("%I:%M:%S %p"),
            now.strftime("%A, %b %d, %Y")
        )

    @Slot()
    def update_system(self):
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_time)
            days, rem = divmod(uptime_seconds, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, _ = divmod(rem, 60)

            net = psutil.net_io_counters()
            sent = net.bytes_sent / (1024 ** 2)
            recv = net.bytes_recv / (1024 ** 2)

            cpu_percent = psutil.cpu_percent()
            ram_total = round(psutil.virtual_memory().total / (1024 ** 3), 2)
            ram_used = round(psutil.virtual_memory().used / (1024 ** 3), 2)

            info = [
                ("Computer", platform.node()),
                ("OS", f"{platform.system()} {platform.release()}"),
                ("Architecture", platform.architecture()[0]),
                ("CPU Usage", f"{cpu_percent}%"),
                ("RAM Usage", f"{ram_used} / {ram_total} GB"),
                ("Uptime", f"{days}d {hours}h {minutes}m"),
                ("Network", f"Sent: {sent:.2f} MB | Recv: {recv:.2f} MB"),
            ]
        except Exception:
            info = []

        self.system_signal.emit(info)

    @Slot()
    def update_user(self):
        # Session elapsed time
        elapsed = int(time.time() - self.session_start)
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)

        # Active processes
        try:
            procs = [p for p in psutil.process_iter(['username', 'cpu_times']) if p.info['username']]
            active_count = len(procs)

            # Total CPU time used by user processes
            cpu_time = sum(sum(p.info['cpu_times'][:2]) for p in procs)  # user + system time
            cpu_hours, rem = divmod(int(cpu_time), 3600)
            cpu_minutes, cpu_seconds = divmod(rem, 60)
        except Exception:
            active_count = 0
            cpu_hours = cpu_minutes = cpu_seconds = 0

        user_info = {
            "session_time": f"{hours}h {minutes}m {seconds}s",
            "active_processes": str(active_count),
            "cpu_time": f"{cpu_hours}h {cpu_minutes}m {cpu_seconds}s"
        }

        self.user_signal.emit(user_info)


class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System & User Stats")
        self.setStyleSheet("""
            QLabel#header {
                font-size: 18px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QLabel#label {
                color: #AAAAAA;
            }
            QLabel#value {
                color: #FFFFFF;
            }
            QWidget {
                background-color: #1E1E1E;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Time & Date ---
        self.time_header = QLabel("Current Time & Date")
        self.time_header.setObjectName("header")
        layout.addWidget(self.time_header)
        self.time_label = QLabel()
        self.time_label.setObjectName("value")
        self.date_label = QLabel()
        self.date_label.setObjectName("value")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.date_label)
        layout.addLayout(time_layout)

        # --- System Stats ---
        self.sys_header = QLabel("System Information")
        self.sys_header.setObjectName("header")
        layout.addWidget(self.sys_header)
        self.system_rows = []
        for _ in range(7):
            row = QHBoxLayout()
            label = QLabel("")
            label.setObjectName("label")
            value = QLabel("")
            value.setObjectName("value")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)
            self.system_rows.append((label, value))

        # --- User Stats ---
        self.user_header = QLabel("User Session Stats")
        self.user_header.setObjectName("header")
        layout.addWidget(self.user_header)

        self.user_rows = {}
        for key in ["Session Time", "Active Processes", "CPU Time Used"]:
            row = QHBoxLayout()
            label = QLabel(key)
            label.setObjectName("label")
            value = QLabel("0")
            value.setObjectName("value")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)
            self.user_rows[key] = value

        # --- Thread Setup ---
        self.thread = QThread(self)
        self.worker = StatsWorker()
        self.worker.moveToThread(self.thread)
        self.worker.time_signal.connect(self.update_time)
        self.worker.system_signal.connect(self.update_system)
        self.worker.user_signal.connect(self.update_user)
        self.thread.start()

        # --- Timers ---
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.worker.update_time)
        self.time_timer.start(500)

        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.worker.update_system)
        self.system_timer.start(5000)

        self.user_timer = QTimer(self)
        self.user_timer.timeout.connect(self.worker.update_user)
        self.user_timer.start(1000)

    @Slot(str, str)
    def update_time(self, t, d):
        self.time_label.setText(t)
        self.date_label.setText(d)

    @Slot(list)
    def update_system(self, info):
        for i, (lbl, val) in enumerate(self.system_rows):
            if i < len(info):
                lbl.setText(info[i][0])
                val.setText(info[i][1])
            else:
                lbl.setText("")
                val.setText("")

    @Slot(dict)
    def update_user(self, data):
        self.user_rows["Session Time"].setText(data["session_time"])
        self.user_rows["Active Processes"].setText(data["active_processes"])
        self.user_rows["CPU Time Used"].setText(data["cpu_time"])

    def closeEvent(self, event):
        self.time_timer.stop()
        self.system_timer.stop()
        self.user_timer.stop()
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stats = StatsWidget()
    stats.show()
    sys.exit(app.exec())