import time

def run_startup(progress_callback):
    progress_callback(0, "Starting...")
    steps = [
        (20, "Initializing...", 1),
        (45, "Loading models...", 1),
        (71, "Loading controllers...", 1),
        (90, "Loading resources...", 1),
        (100, "Enjoy!", 1),
    ]
    last_progress = 0
    for target, message, duration in steps:
        increments = max(1, target - last_progress)
        for p in range(last_progress + 1, target + 1):
            progress_callback(p, message)
            time.sleep(duration / increments)
        last_progress = target

