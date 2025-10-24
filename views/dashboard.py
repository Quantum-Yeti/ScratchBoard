from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
from datetime import datetime
from utils.resource_path import resource_path

class StatCard(QFrame):
    """A dark stat card with animated numeric value."""
    def __init__(self, title, value="0"):
        super().__init__()
        self._value = 0
        self._display_value = QLabel(value)
        self._display_value.setAlignment(Qt.AlignCenter)

        self.setObjectName("StatCard")
        self.setStyleSheet("""
            QFrame#StatCard {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                color: #2b2b2b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #fff;")

        self._display_value.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #4c8caf;"
        )

        layout.addWidget(title_label)
        layout.addWidget(self._display_value)

    # Property for animation
    def _set_value(self, val):
        self._value = val
        self._display_value.setText(str(int(val)))

    def _get_value(self):
        return self._value

    value = Property(float, _get_value, _set_value)


class DashboardView(QWidget):
    def __init__(self, model, image_path=None):
        super().__init__()
        self.model = model
        self.image_path = resource_path(image_path) if image_path else None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # --- Banner ---
        if image_path:
            self.banner = QLabel()
            self.banner.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.banner)
            self.update_banner()

        # --- Stat cards ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        main_layout.addLayout(stats_layout)

        self.cards = {
            "total": StatCard("Total Notes"),
            "cats": StatCard("Categories"),
            "avg": StatCard("Avg Length"),
        }
        for c in self.cards.values():
            stats_layout.addWidget(c)

        # --- Charts Layout ---
        charts_layout = QHBoxLayout()
        main_layout.addLayout(charts_layout)

        self.line_figure = Figure(figsize=(5, 4), dpi=100)
        self.line_canvas = FigureCanvas(self.line_figure)
        charts_layout.addWidget(self.line_canvas)

        self.scatter_figure = Figure(figsize=(5, 4), dpi=100)
        self.scatter_canvas = FigureCanvas(self.scatter_figure)
        charts_layout.addWidget(self.scatter_canvas)

        # Initial data
        self.update_stats(animated=False)
        self.update_graphs()

    #   STATS
    def update_stats(self, animated=True):
        """Recalculate and optionally animate the top stats."""
        categories = self.model.get_all_categories()
        all_notes = []
        for c in categories:
            all_notes.extend(self.model.get_notes(category_name=c))

        total = len(all_notes)
        avg_len = int(sum(len(n["content"]) for n in all_notes) / total) if total else 0
        cats = len(categories)

        values = {
            "total": total,
            "cats": cats,
            "avg": avg_len,
        }

        for key, val in values.items():
            card = self.cards[key]
            if animated:
                self.animate_card_value(card, val)
            else:
                card._set_value(val)

    def animate_card_value(self, card, new_value):
        """Smoothly count the number up/down."""
        anim = QPropertyAnimation(card, b"value", self)
        anim.setDuration(800)
        anim.setStartValue(card.value)
        anim.setEndValue(new_value)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        # Keep reference alive to prevent garbage collection
        card._anim = anim

    # GRAPHS
    def update_graphs(self):
        self.update_line_chart()
        self.update_scatter_plot()

    def update_line_chart(self):
        self.line_figure.clear()
        ax = self.line_figure.add_subplot(111)
        ax.set_facecolor("#2b2b2b")
        self.line_figure.patch.set_facecolor("#2b2b2b")

        categories = self.model.get_all_categories()
        data = defaultdict(list)

        for cat in categories:
            notes = self.model.get_notes(category_name=cat, order_by="created ASC")
            dates = [datetime.fromisoformat(n["created"]).date() for n in notes]
            cumulative = 0
            by_date = defaultdict(int)
            for d in sorted(dates):
                cumulative += 1
                by_date[d] = cumulative
            x = list(by_date.keys())
            y = list(by_date.values())
            data[cat] = (x, y)

        for cat, (x, y) in data.items():
            ax.plot(x, y, marker='o', label=cat)

        ax.set_title("Cumulative Notes Over Time", color="#e0e0e0")
        ax.set_xlabel("Date", color="#e0e0e0")
        ax.set_ylabel("Total Notes", color="#e0e0e0")
        ax.legend()
        ax.tick_params(colors="#e0e0e0")
        self.line_canvas.draw()

    def update_scatter_plot(self):
        self.scatter_figure.clear()
        ax = self.scatter_figure.add_subplot(111)
        ax.set_facecolor("#2b2b2b")
        self.scatter_figure.patch.set_facecolor("#2b2b2b")

        categories = self.model.get_all_categories()
        for cat in categories:
            notes = self.model.get_notes(category_name=cat, order_by="created ASC")
            x = list(range(1, len(notes) + 1))
            y = [len(n["content"]) for n in notes]
            ax.scatter(x, y, label=cat)

        ax.set_title("Note Length vs. Creation Order", color="#e0e0e0")
        ax.set_xlabel("Note Index", color="#e0e0e0")
        ax.set_ylabel("Content Length", color="#e0e0e0")
        ax.legend()
        ax.tick_params(colors="#e0e0e0")
        self.scatter_canvas.draw()

    # BANNER
    def update_banner(self):
        """Load and scale the banner image using resource_path."""
        if not self.image_path:
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            print(f"⚠️ Failed to load banner image: {self.image_path}")
            return

        max_width = self.width() - 24
        max_height = self.height() // 4
        scaled_pixmap = pixmap.scaled(
            max_width,
            max_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.banner.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "banner"):
            self.update_banner()
