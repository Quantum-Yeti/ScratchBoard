from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from helpers.dashboard_stats import calculate_stats

class StatCard(QWidget):
    def __init__(self, title, value="0"):
        super().__init__()
        self._value = 0
        self._display_value = QLabel(value, alignment=Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title, alignment=Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #fff;")
        self._display_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #4c8caf;")

        layout.addWidget(title_label)
        layout.addWidget(self._display_value)

    def _set_value(self, val):
        self._value = val
        self._display_value.setText(str(int(val)))

    def _get_value(self):
        return self._value

    value = Property(float, _get_value, _set_value)


class StatsWidget(QWidget):
    """Container for multiple StatCard widgets"""
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.cards = {}

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create cards
        for key, title in [("total", "Total Notes"),
                           ("cats", "Categories"),
                           ("monthly", "Notes This Month")]:
            card = StatCard(title)
            layout.addWidget(card)
            self.cards[key] = card

    def refresh(self, animated=True):
        """Update all stat cards from the model"""
        values = calculate_stats(self.model)
        for key, val in values.items():
            card = self.cards.get(key)
            if not card:
                continue

            if animated:
                anim = QPropertyAnimation(card, b"value", self)
                anim.setDuration(700)
                anim.setStartValue(card.value)
                anim.setEndValue(val)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                anim.start()
                card._anim = anim
            else:
                card._set_value(val)
