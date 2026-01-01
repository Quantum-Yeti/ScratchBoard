from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import QObject, QEvent

class ContextMenuStyler(QObject):
    """
    Event filter that applies a dark powder-blue theme to all context menus.
    """
    def eventFilter(self, obj, event):
        # Only intercept QEvent.Type.Show events
        if event.type() == QEvent.Type.Show and isinstance(obj, QMenu):
            obj.setStyleSheet("""
                QMenu {
                    background-color: #222;       /* Dark background */
                    color: #B0E0E6;              /* Powder blue text */
                    border: 1px solid #555;      /* Subtle border */
                }
                QMenu::item:selected {
                    background-color: #4A6B8A;   /* Darker powder blue highlight */
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background: #555;
                    margin: 5px 0;
                }
            """)
        return super().eventFilter(obj, event)
