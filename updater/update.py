import os
import sys
import time
import shutil
import subprocess

def main():
    # Arguments: updater.py <new_exe> <current_exe>
    if len(sys.argv) < 3:
        print("Usage: updater.py <new_exe> <current_exe>")
        sys.exit(1)

    new_exe = sys.argv[1]
    current_exe = sys.argv[2]

    # Wait for the main app to close
    while True:
        try:
            # Try renaming to check if it's unlocked
            os.rename(current_exe, current_exe)
            break
        except OSError:
            time.sleep(0.5)

    # Replace old exe with new exe
    try:
        shutil.move(new_exe, current_exe)
    except Exception as e:
        print("Failed to replace executable:", e)
        sys.exit(1)

    # Relaunch app
    subprocess.Popen([current_exe])
    sys.exit()

if __name__ == "__main__":
    main()
