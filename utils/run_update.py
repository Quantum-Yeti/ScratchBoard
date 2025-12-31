import os
import subprocess

from PySide6.QtWidgets import QMessageBox


def run_update_batch_file(self):
    """Run the batch file to update the application."""
    try:
        # Get the path of the 'update.bat' file inside the 'utils' directory
        batch_file_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'update_exe.bat')
        batch_file_path = os.path.abspath(batch_file_path)  # Convert to absolute path for safety

        # Print the path for debugging purposes
        print(f"Batch file path: {batch_file_path}")

        # Check if the batch file exists
        if not os.path.exists(batch_file_path):
            raise FileNotFoundError(f"Batch file not found: {batch_file_path}")

        # Run the batch file using subprocess
        subprocess.run([batch_file_path], check=True, shell=True)
        QMessageBox.information(self, "Update", "Application update initiated. Please wait while the app updates.")
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(self, "Error", f"Failed to run the update batch file:\n{str(e)}")
    except FileNotFoundError as fnf_error:
        QMessageBox.critical(self, "Error", f"Batch file not found:\n{str(fnf_error)}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")