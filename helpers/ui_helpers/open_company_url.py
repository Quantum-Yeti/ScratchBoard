# Get company website
import webbrowser

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

def open_company_homepage(url: str | None) -> None:
    """
    Open the company homepage URL in the default browser.

    Args:
        url (str | None): The URL to open. Does nothing if None or empty.
    """
    if url:
        QDesktopServices.openUrl(QUrl(url))