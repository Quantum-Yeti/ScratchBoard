from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from utils.resource_path import resource_path
from helpers.calc_helpers.dashboard_stats import calculate_stats  # Make sure this returns new stats like avg words


class StatCard(QWidget):
    """Dashboard stat card with animated value."""
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
    """Container for multiple StatCard widgets."""
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.cards = {}

        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create cards. You can add avg word count here
        for key, title in [
            ("total", "Total Notes"),
            ("monthly", "Notes This Month"),
            ("avg_words", "Avg Words/Note"),
            ("longest_note", "Longest Note"),
            ("shortest_note", "Shortest Note"),
            ("today", "Notes Today")
        ]:
            card = StatCard(title)
            layout.addWidget(card)
            self.cards[key] = card

    def refresh(self, animated=True):
        """Update all stat cards from the model."""
        values = calculate_stats(self.model)  # should return {'total': X, 'avg_words': Y, 'monthly': Z}

        for key, val in values.items():
            card = self.cards.get(key)
            if not card:
                continue

            if animated:
                anim = QPropertyAnimation(card, b"value", self)
                anim.setDuration(700)
                anim.setStartValue(card.value)
                anim.setEndValue(val)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.start()
                card._anim = anim
            else:
                card._set_value(val)

    def load_stylesheet(self):
        """Load dark theme QSS."""
        try:
            with open(resource_path("ui/themes/main_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load main_theme.qss:", e)