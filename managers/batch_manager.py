import subprocess

import psutil

PROTECTED_PROCESSES = {
    "explorer.exe",
    "wininit.exe",
    "winlogon.exe",
    "csrss.exe",
    "services.exe",
    "lsass.exe",
    "system"
}

class BatchManager:

    @staticmethod
    def list_processes():
        processes = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = proc.info["name"]
                pid = proc.info["pid"]
                if name:
                    processes.append((name.lower(), pid))
            except psutil.NoSuchProcess:
                pass
        return sorted(processes)

    @staticmethod
    def is_protected(name: str) -> bool:
        return name.lower() in PROTECTED_PROCESSES

    @staticmethod
    def kill_pid(pid: int):
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            check=True,
            capture_output=True,
            text=True
        )