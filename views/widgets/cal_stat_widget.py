import datetime
import psutil

from PySide6.QtCore import QTimer, Qt, QObject, Slot, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QProgressBar, QFrame, QHBoxLayout, QDialog, QTextEdit
)

from ui.themes.cal_stat_theme import cal_stat_style


class ProcessWorker(QObject):
    stats_arm = Signal(int, int)
    process_arm = Signal(list)
    disk_arm = Signal(str)
    net_arm = Signal(str)
    users_arm = Signal(str)

    @Slot()
    def get_stats(self):
        try:
            cpu = int(psutil.cpu_percent())
            ram = int(psutil.virtual_memory().percent)
        except Exception:
            cpu = 0
            ram = 0

        self.stats_arm.emit(cpu, ram)

    @Slot()
    def get_process(self):
        processes = []

        for proc in psutil.process_iter(attrs=["name", "cpu_percent"]):
            try:
                name = proc.info["name"]
                cpu = int(proc.info["cpu_percent"])

                if not name or not cpu:
                    continue
                if "idle" in name.lower():
                    continue

                processes.append([name, cpu])

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda p: p[1], reverse=True)
        self.process_arm.emit(processes[:5])

# --- Dialog for Live Stats ---
class StatsDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    @Slot(str)
    def update_text(self, content):
        self.text.setPlainText(content)

class CalStatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Cal + CPU Stats")
        self.setStyleSheet(cal_stat_style)

        # Main Vertical Layout
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
        stats_frame.setFrameShape(QFrame.Shape.NoFrame)

        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(6)

        # CPU Row
        cpu_row = QHBoxLayout()
        cpu_row.setContentsMargins(0, 0, 0, 0)
        cpu_row.setSpacing(8)

        cpu_label = QLabel("CPU", self)
        cpu_label.setStyleSheet("font-weight: bold; color: #B8F1B0;")
        cpu_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cpu_label.setFixedWidth(35)  # keeps labels aligned

        self.cpu_bar = QProgressBar(self)
        self.cpu_bar.setFormat("%p%")

        cpu_row.addWidget(cpu_label)
        cpu_row.addWidget(self.cpu_bar, 1)

        # RAM Row
        ram_row = QHBoxLayout()
        ram_row.setContentsMargins(0, 0, 0, 0)
        ram_row.setSpacing(8)

        ram_label = QLabel("RAM", self)
        ram_label.setStyleSheet("font-weight: bold; color: #B8F1B0;")
        ram_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        ram_label.setFixedWidth(35)

        self.ram_bar = QProgressBar(self)
        self.ram_bar.setFormat("%p%")

        ram_row.addWidget(ram_label)
        ram_row.addWidget(self.ram_bar, 1)

        # Add rows to stats layout
        stats_layout.addLayout(cpu_row)
        stats_layout.addLayout(ram_row)

        # Add stats frame to main layout
        layout.addWidget(stats_frame)

        # Process section
        process_frame = QFrame(self)
        process_layout = QVBoxLayout(process_frame)
        process_layout.setSpacing(0)
        process_layout.setContentsMargins(0, 0, 0, 0)

        self.process_header = QLabel(process_frame)
        self.process_header.setObjectName("process_header")
        self.process_header.setAlignment(Qt.AlignCenter)
        process_layout.addWidget(self.process_header)

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
            row_layout.addWidget(cpu_lbl)

            self.process_rows.append((name_lbl, cpu_lbl))
            process_layout.addWidget(row)

        # Add the frame for the process box
        layout.addWidget(process_frame)

        self.users_label = QLabel(self)
        self.users_label.setStyleSheet("font-weight: bold; color: #ADFF2F;")
        self.users_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.users_label)

        # Set up thread
        self.psutil_thread = QThread(self)
        self.psutil_worker = ProcessWorker()
        self.psutil_worker.moveToThread(self.psutil_thread)

        # Connect to thread signals
        self.psutil_worker.stats_arm.connect(self.on_stats_ready)
        self.psutil_worker.process_arm.connect(self.on_processes_ready)

        # Start thread
        self.psutil_thread.start()

        # Thread Timers
        self.timer_clock = QTimer(self)
        self.timer_clock.timeout.connect(self.update_time)
        self.timer_clock.timeout.connect(self.psutil_worker.get_stats)
        self.timer_clock.start(500)

        self.timer_processes = QTimer(self)
        self.timer_processes.timeout.connect(self.psutil_worker.get_process)
        self.timer_processes.start(6000)

        # Call time update
        self.update_time()

    # UI Slots for Thread
    @Slot(int, int)
    def on_stats_ready(self, cpu, ram):
        self.cpu_bar.setValue(cpu)
        self.ram_bar.setValue(ram)

    @Slot(list)
    def on_processes_ready(self, processes):
        for i, (name_lbl, cpu_lbl) in enumerate(self.process_rows):
            if i < len(processes):
                name, cpu = processes[i]
                name_lbl.setText(name)
                cpu_lbl.setText(f"{cpu:.1f}%")
            else:
                name_lbl.setText("-")
                cpu_lbl.setText("")

    # Update Functions
    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))

    # Clean up thread events
    def closeEvent(self, event):
        self.psutil_thread.quit()
        self.psutil_thread.wait()
        super().closeEvent(event)
