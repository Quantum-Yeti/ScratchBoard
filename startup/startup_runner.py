import time

def run_startup(progress_callback):
    """
    Simulates (since it's a one-file bundled exe with PyInstaller) a startup sequence with progress updates.
    """

    # Initial progress message at 0%
    progress_callback(0, "Starting...")

    # Define sequence of startup steps
    steps = [
        (20, "Initializing...", 1),
        (45, "Loading models...", 1),
        (71, "Loading controllers...", 1),
        (90, "Loading resources...", 1),
        (100, "Enjoy!", 1),
    ]

    last_progress = 0 # Keep track of last progress percent

    # Iterate over each startup step
    for target, message, duration in steps:

        # Calculate  how many increments to divide the duration into
        increments = max(1, target - last_progress)

        # Gradually increase progress from last_progress + 1
        for p in range(last_progress + 1, target + 1):

            # Call the progress callback with current progress and it's message
            progress_callback(p, message)

            # Sleep for a fraction of the step duration for even spread
            time.sleep(duration / increments)

        # Update last_progress for the next step
        last_progress = target

