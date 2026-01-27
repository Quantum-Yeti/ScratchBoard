from pathlib import Path
import shutil
import sys
import subprocess
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

class NukeService:
    RESET_FLAG = Path(".scratchboard_reset")
    DATA_DIR = Path("sb_data")

    @classmethod
    def request_reset_and_restart(cls, delay_ms=500):
        # Write reset flag
        cls.RESET_FLAG.write_text("reset")

        # Schedule restart AFTER the current event loop exits
        QTimer.singleShot(delay_ms, cls._restart_app)

        # Exit the current app gracefully
        QApplication.quit()

    @staticmethod
    def _restart_app():
        python = sys.executable
        subprocess.Popen([python] + sys.argv)

    @classmethod
    def handle_startup_reset(cls):
        if not cls.RESET_FLAG.exists():
            return

        try:
            if cls.DATA_DIR.exists():
                shutil.rmtree(cls.DATA_DIR)
        except Exception as e:
            print("Reset failed:", e)
        finally:
            cls.RESET_FLAG.unlink(missing_ok=True)

        # Recreate folders
        (cls.DATA_DIR / "db").mkdir(parents=True, exist_ok=True)
        (cls.DATA_DIR / "images").mkdir(parents=True, exist_ok=True)
        (cls.DATA_DIR / "notepad").mkdir(parents=True, exist_ok=True)

        print("Reset complete: Everything nuked. Reopen the app please.")
