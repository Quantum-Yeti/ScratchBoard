import time

def run_startup(progress_callback):
    """Run initialization steps with progress updates on splash screen."""
    import time

    steps = [
        ("Initializing...", lambda: time.sleep(1)),
        ("Loading models...", lambda: time.sleep(1)),
        ("Loading controllers...", lambda: time.sleep(1)),
        ("Loading resources...", lambda: time.sleep(1)),
        ("Finishing...", lambda: time.sleep(1)),
    ]

    total = len(steps)
    for i, (message, action) in enumerate(steps, start=1):
        progress = int((i / total) * 100)
        progress_callback(progress, message)  # Emit progress to splash screen
        action()
