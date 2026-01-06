from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit, QMessageBox, QWidget
import subprocess
import psutil
from managers.batch_manager import BatchManager
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.resource_path import resource_path


class BatchWidget(QWidget):

    def __init__(self, model=None, parent=None):
        super().__init__(parent)
        self.model = model

        # Vertical box layout
        layout = QVBoxLayout(self)

        # Process selector layout
        proc_layout = QHBoxLayout()
        proc_layout.addWidget(QLabel("Select Process:"))

        self.process_combo = QComboBox()
        self.process_combo.setStyleSheet(vertical_scrollbar_style +
                                         "QComboBox QAbstractItemView {background-color: #222;}"
                                         )
        proc_layout.addWidget(self.process_combo)

        # Refresh task list
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon(resource_path("resources/icons/refresh_green.png")))
        refresh_btn.setFixedWidth(30)
        refresh_btn.clicked.connect(self.refresh_processes)
        proc_layout.addWidget(refresh_btn)

        layout.addLayout(proc_layout)

        # Execute tasks buttons
        self.kill_btn = QPushButton("Stop Process -> terminate a process from the list")
        self.kill_btn.setIcon(QIcon(resource_path("resources/icons/stop.png")))
        self.kill_btn.clicked.connect(self.on_kill_clicked)
        layout.addWidget(self.kill_btn)

        self.kill_restart_btn = QPushButton("Stop/Restart Process -> terminate a process from the list then restart it")
        self.kill_restart_btn.setIcon(QIcon(resource_path("resources/icons/start.png")))
        self.kill_restart_btn.clicked.connect(self.on_kill_restart_clicked)
        layout.addWidget(self.kill_restart_btn)

        self.kill_children_btn = QPushButton("Stop Child Processes -> terminate spawned child processes")
        self.kill_children_btn.setIcon(QIcon(resource_path("resources/icons/stop_two.png")))
        self.kill_children_btn.clicked.connect(self.on_kill_child_processes_clicked)
        layout.addWidget(self.kill_children_btn)

        self.suspend_btn = QPushButton("Suspend Process -> pause a process")
        self.suspend_btn.setIcon(QIcon(resource_path("resources/icons/pause.png")))
        self.suspend_btn.clicked.connect(self.on_suspend_clicked)
        layout.addWidget(self.suspend_btn)

        self.resume_btn = QPushButton("Resume Process -> resume a process")
        self.resume_btn.setIcon(QIcon(resource_path("resources/icons/resume.png")))
        self.resume_btn.clicked.connect(self.on_resume_clicked)
        layout.addWidget(self.resume_btn)

        self.open_folder_btn = QPushButton("Open Executable Folder -> open the folder path to the process")
        self.open_folder_btn.setIcon(QIcon(resource_path("resources/icons/open_folder.png")))
        self.open_folder_btn.clicked.connect(self.on_open_folder_clicked)
        layout.addWidget(self.open_folder_btn)

        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.refresh_processes()

    # Helper methods
    def refresh_processes(self):
        """List all running processes in the combo box."""
        self.process_combo.clear()
        for name, pid in BatchManager.list_processes():
            self.process_combo.addItem(f"{name} (PID {pid})", pid)

    def on_kill_clicked(self):
        """Kill the selected process."""
        pid = self.process_combo.currentData()
        label = self.process_combo.currentText()

        if pid is None:
            return

        name = label.split(" (")[0]

        if BatchManager.is_protected(name):
            QMessageBox.critical(self, "Blocked", f"{name} is a protected system process.")
            return

        confirm = QMessageBox.question(self, "Confirm", f"Terminate process:\n\n{label} ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            BatchManager.kill_pid(pid)
            self.output.setPlainText(f"✔ Successfully terminated {label}")
            self.refresh_processes()
        except Exception as e:
            self.output.setPlainText(str(e))

    def on_kill_restart_clicked(self):
        """Kill and restart the selected process using its executable path."""
        pid = self.process_combo.currentData()
        label = self.process_combo.currentText()

        if pid is None:
            return

        name = label.split(" (")[0]

        if BatchManager.is_protected(name):
            QMessageBox.critical(
                self,
                "Blocked",
                f"{name} is a protected system process and cannot be restarted."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            f"Terminate and restart process:\n\n{label} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # Get process executable path
            proc = psutil.Process(pid)
            exe_path = proc.exe()  # full path to the exe

            # Kill process
            BatchManager.kill_pid(pid)

            # Restart process
            subprocess.Popen([exe_path])

            self.output.setPlainText(f"✔ Successfully terminated and restarted {label}")
            self.refresh_processes()

        except psutil.NoSuchProcess:
            self.output.setPlainText("Process no longer exists.")
            self.refresh_processes()
        except Exception as e:
            self.output.setPlainText(f"Failed to restart: {e}")

    def on_kill_child_processes_clicked(self):
        """Terminate all child processes of the selected process."""
        pid = self.process_combo.currentData()
        label = self.process_combo.currentText()

        if pid is None:
            return

        name = label.split(" (")[0]

        if BatchManager.is_protected(name):
            QMessageBox.critical(
                self,
                "Blocked",
                f"{name} is a protected system process; children cannot be terminated."
            )
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            f"Terminate all child processes of:\n\n{label} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)

            if not children:
                self.output.setPlainText("No child processes found.")
                return

            for child in children:
                child.terminate()  # Send terminate signal
            gone, alive = psutil.wait_procs(children, timeout=3)

            self.output.setPlainText(
                f"✔ Terminated {len(gone)} child process(es) of {label}."
            )
            self.refresh_processes()

        except psutil.NoSuchProcess:
            self.output.setPlainText("Process no longer exists.")
            self.refresh_processes()
        except Exception as e:
            self.output.setPlainText(f"Failed to terminate children: {e}")

    def on_suspend_clicked(self):
        """Suspend the selected process."""
        pid = self.process_combo.currentData()
        if not pid:
            return
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            self.output.setPlainText(f"✔ Suspended {proc.name()} (PID {pid})")
        except Exception as e:
            self.output.setPlainText(f"Failed to suspend process: {e}")

    def on_resume_clicked(self):
        """Resume the selected process."""
        pid = self.process_combo.currentData()
        if not pid:
            return
        try:
            proc = psutil.Process(pid)
            proc.resume()
            self.output.setPlainText(f"✔ Resumed {proc.name()} (PID {pid})")
        except Exception as e:
            self.output.setPlainText(f"Failed to resume process: {e}")

    def on_open_folder_clicked(self):
        """Open the folder of the executable."""
        pid = self.process_combo.currentData()
        if not pid:
            return
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            folder_path = str(exe_path.rsplit("\\", 1)[0])
            subprocess.Popen(f'explorer "{folder_path}"')
            self.output.setPlainText(f"✔ Opened folder: {folder_path}")
        except Exception as e:
            self.output.setPlainText(f"Failed to open folder: {e}")
