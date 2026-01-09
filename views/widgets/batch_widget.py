from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTextEdit, QMessageBox, QGridLayout, QFrame, QDialog
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QThread, QSize

from managers.batch_manager import BatchManager
from helpers.ui_helpers.batch_worker import BatchWorker
from utils.custom_context_menu import ContextMenuUtility
from utils.resource_path import resource_path
from ui.themes.scrollbar_style import vertical_scrollbar_style


class BatchWidget(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._threads = []

        self._build_ui()
        self.refresh_processes()

    # Build UI
    def _build_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Select Process:"))

        self.process_combo = QComboBox()
        self.process_combo.setStyleSheet(
            vertical_scrollbar_style +
            """
            QComboBox {
                border: 1px solid #1E90FF;          
                padding: 4px 8px;            
                background-color: #111;      
                color: #fff;            
            }
            QComboBox QAbstractItemView {
                background-color: #111;
                selection-background-color: #1E90FF;
                color: #fff;
            }
            """
        )
        font = self.process_combo.font()
        font.setPointSize(13)
        self.process_combo.setFont(font)
        top.addWidget(self.process_combo)

        refresh = QPushButton()
        refresh.setIcon(QIcon(resource_path("resources/icons/refresh_green.png")))
        refresh.setStyleSheet("text-align: center;")
        refresh.setFixedSize(30, 30)
        refresh.clicked.connect(self.refresh_processes)
        top.addWidget(refresh)

        layout.addLayout(top)

        # Button grid 3x3
        button_grid = QGridLayout()
        button_grid.setSpacing(8)

        buttons = [
            ("Stop Process", "stop.png", self.kill),
            ("Stop && Restart", "start.png", self.kill_restart),
            ("Stop Children", "stop_two.png", self.kill_children),
            ("Suspend Process", "pause.png", self.suspend),
            ("Resume Process", "resume.png", self.resume),
            ("Open Exe Folder", "open_folder.png", self.open_folder),
        ]

        for index, (text, icon, handler) in enumerate(buttons):
            row = index // 3
            col = index % 3
            btn = QPushButton(text)
            btn.setIcon(QIcon(resource_path(f"resources/icons/{icon}")))
            btn.setIconSize(QSize(22, 22))
            btn.setStyleSheet("text-align: center;")
            btn.clicked.connect(handler)
            button_grid.addWidget(btn, row, col)

        layout.addLayout(button_grid)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Output box
        self.output = QTextEdit(readOnly=True)
        self.output.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.output)

        # Override context menu
        self.context_menu = ContextMenuUtility(self.output)

    @staticmethod
    def _add_button(layout, text, icon, handler):
        btn = QPushButton(text)
        btn.setIcon(QIcon(resource_path(f"resources/icons/{icon}")))
        btn.clicked.connect(handler)
        layout.addWidget(btn)

    # Thread helpers
    def run_threaded(self, fn, *args) -> None:
        thread = QThread()
        worker = BatchWorker(fn, *args)

        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self.on_success)
        worker.error.connect(self.on_error)

        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)

        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # important: keep references
        self._threads.append((thread, worker))

        # cleanup safely
        def cleanup():
            try:
                self._threads.remove((thread, worker))
            except ValueError:
                pass

        thread.finished.connect(cleanup)

        thread.start()

    # Thread slots
    def on_success(self, msg):
        self.output.setPlainText(msg)
        self.refresh_processes()

    def on_error(self, msg):
        self.output.setPlainText(f"❌ {msg}")

    # Logic
    def refresh_processes(self):
        self.process_combo.clear()
        for name, pid in BatchManager.list_processes():
            self.process_combo.addItem(f"{name} (PID {pid})", pid)

    def _selected_pid(self):
        return self.process_combo.currentData()

    def _confirm(self, text):
        return QMessageBox.question(
            self, "Confirm", text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

    def _blocked(self, name):
        QMessageBox.critical(self, "Blocked", f"{name} is protected.")

    # Action functions
    def kill(self) -> None:
        pid = self._selected_pid()
        if not pid:
            return None
        name = self.process_combo.currentText().split(" (")[0]
        if BatchManager.is_protected(name):
            self._blocked(name)
            return None
        if self._confirm(f"Terminate {name}?"):
            self.output.setPlainText("Working...")
            self.run_threaded(BatchManager.kill_pid, pid)

        return None

    def kill_restart(self) -> None:
        pid = self._selected_pid()
        if not pid:
            return None
        name = self.process_combo.currentText().split(" (")[0]
        if BatchManager.is_protected(name):
            self._blocked(name)
            return None
        if self._confirm(f"Restart {name}?"):
            self.output.setPlainText("Working...")
            self.run_threaded(BatchManager.kill_and_restart, pid)

        return None

    def kill_children(self):
        pid = self._selected_pid()
        if pid:
            self.output.setPlainText("Working...")
            self.run_threaded(BatchManager.kill_children, pid)

    def suspend(self):
        pid = self._selected_pid()
        if pid:
            self.run_threaded(BatchManager.suspend, pid)

    def resume(self):
        pid = self._selected_pid()
        if pid:
            self.run_threaded(BatchManager.resume, pid)

    def open_folder(self):
        pid = self._selected_pid()
        if pid:
            self.run_threaded(BatchManager.open_folder, pid)
