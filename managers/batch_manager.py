import subprocess
import psutil

PROTECTED_PROCESSES = {
    "explorer.exe",
    "wininit.exe",
    "winlogon.exe",
    "csrss.exe",
    "services.exe",
    "lsass.exe",
    "system",
    "smss.exe",
    "dwm.exe",
    "taskhostw.exe",
    "svchost.exe",
    "spoolsv.exe"
}


class BatchManager:

    @staticmethod
    def list_processes():
        processes = []
        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                name = proc.info["name"]
                exe = proc.info["exe"]
                if not name or not exe:
                    continue # Skip processes with no name or no executable

                if name.lower() in PROTECTED_PROCESSES:
                    continue # skip critical os processes


                processes.append(
                    (proc.info["name"].lower(), proc.info["pid"])
                )

            except psutil.NoSuchProcess:
                pass # skip processes that can not be accessed
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
        return f"✔ Terminated PID {pid}"

    @staticmethod
    def kill_and_restart(pid: int):
        proc = psutil.Process(pid)
        exe = proc.exe()
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
        subprocess.Popen([exe])
        return f"✔ Restarted {exe}"

    @staticmethod
    def kill_children(pid: int):
        proc = psutil.Process(pid)
        children = proc.children(recursive=True)

        if not children:
            return "No child processes found."

        for child in children:
            child.terminate()

        gone, alive = psutil.wait_procs(children, timeout=3)
        return f"✔ Terminated {len(gone)} child process(es)"

    @staticmethod
    def suspend(pid: int):
        psutil.Process(pid).suspend()
        return f"✔ Suspended PID {pid}"

    @staticmethod
    def resume(pid: int):
        psutil.Process(pid).resume()
        return f"✔ Resumed PID {pid}"

    @staticmethod
    def open_folder(pid: int):
        exe = psutil.Process(pid).exe()
        folder = exe.rsplit("\\", 1)[0]
        subprocess.Popen(f'explorer "{folder}"')
        return f"✔ Opened {folder}"
