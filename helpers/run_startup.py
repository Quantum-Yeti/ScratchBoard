import time
from views.splash_screen import SplashScreen
from utils.resource_path import configure_matplotlib

def run_startup(splash):
    """Run initialization steps with progress updates on splash screen."""

    steps = [
        ("Initializing...", configure_matplotlib),
        ("Loading modules...", lambda: time.sleep(1)),
        ("Starting controllers...", lambda: time.sleep(1)),
        ("Finalizing...", lambda: time.sleep(0.5)),
    ]

    total = len(steps)
    for i, (message, action) in enumerate(steps, start=1):
        progress = int((i / total) * 100)
        splash.set_progress(progress, message)
        action()  # Execute step