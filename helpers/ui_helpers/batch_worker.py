from PySide6.QtCore import QObject, Signal, Slot


class BatchWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self.fn = fn
        self.args = args

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args)
            # emit finished
            self.finished.emit(result if result is not None else "✔ Done")
        except Exception as e:
            self.error.emit(str(e))
