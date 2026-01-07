from PySide6.QtCore import QUrl, QSettings
from PySide6.QtGui import QMouseEvent, QDesktopServices, Qt
from PySide6.QtWidgets import QPushButton, QInputDialog


class LogoButton(QPushButton):
    """
    Subclass for the sidebar logo button that:
        - Left-click: opens a URL in the default browser
        - Right-click: prompts the user to enter a new URL
    Stores the URL persistently using QSettings
    """
    def __init__(self, text="", settings_key="logo_btn_url", default_url="", parent=None, user=None):
        super().__init__(text, parent)
        self.settings_key = settings_key
        self.settings = QSettings(f"{user or 'DefaultUser'}", "ScratchBoard")

        # Load stored URL or use default, ensure it's a string
        self.url = str(self.settings.value(self.settings_key, default_url) or "")

        # Call the tooltip helper
        self._update_tooltip()

    def _update_tooltip(self):
        """Update the tooltip to include the current URL."""
        base_text = self.text() or "Logo"
        if self.url:
            self.setToolTip(f"Welcome, {base_text}!\nLeft-click opens | Right-click edits\nCurrent URL: {self.url}")
        else:
            self.setToolTip(f"Welcome, {base_text}!\nLeft-click opens | Right-click edits\nNo URL set")

    def mousePressEvent(self, event: QMouseEvent):
        """
        Left click -> opens a URL in the default browser.
        Right-click -> prompts the user to enter a new URL.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.url:
                QDesktopServices.openUrl(QUrl(self.url))

        elif event.button() == Qt.MouseButton.RightButton:
            # Create a non-static input dialog
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Change Button Link")
            dialog.setLabelText("Enter a new URL:")
            dialog.setTextValue(self.url)

            # Adjust size of the popup dialog
            dialog.resize(300, 100)

            # Position the dialog to the right of the button
            pos = self.mapToGlobal(self.rect().topRight())
            pos.setX(pos.x() + 20)
            pos.setY(pos.y() - 100)
            dialog.move(pos)

            # Show dialog modally at this position
            if dialog.exec():  # returns True if OK pressed
                new_url = dialog.textValue()
                if new_url:
                    self.url = new_url
                    self.settings.setValue(self.settings_key, self.url)
                    self._update_tooltip()

        else:
            super().mousePressEvent(event)