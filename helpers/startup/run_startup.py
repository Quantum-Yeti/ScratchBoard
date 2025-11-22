import time


def run_startup(splash):
    """Run initialization steps with progress updates on splash screen."""
    steps = [
        ("Initializing...", lambda: time.sleep(1)),
        ("Loading models...", lambda: time.sleep(1)),
        ("Loading controllers...", lambda: time.sleep(1)),
        ("Loading resources...", lambda: time.sleep(1)),
        ("Finishing...", lambda: time.sleep(0.5)),
    ]

    total = len(steps)
    for i, (message, action) in enumerate(steps, start=1):
        progress = int((i / total) * 100)
        splash.set_progress(progress, message)
        action()  # Executes steps