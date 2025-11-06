import os
import sys
from datetime import datetime

import numpy as np
import matplotlib
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.resource_path import resource_path, configure_matplotlib

from helpers.dashboard_stats import calculate_stats
from views.recent_note_view import RecentNoteView
from views.time_clock import TimezoneClock

# Force QtAgg backend for PySide6
matplotlib.use("QtAgg")

# Fix datapath for PyInstaller
try:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    mpl_data_path = os.path.join(base_path, "mpl-data")
    if os.path.exists(mpl_data_path):
        matplotlib.rcParams["datapath"] = mpl_data_path
        print(f"[Matplotlib] datapath set to: {mpl_data_path}")
    else:
        print("[Matplotlib] mpl-data folder not found, using default.")
except Exception as e:
    print(f"[Matplotlib] configuration skipped: {e}")


class StatCard(QFrame):
    """A dark stat card with animated numeric value."""

    def __init__(self, title, value="0"):
        super().__init__()
        self._value = 0
        self._display_value = QLabel(value, alignment=Qt.AlignCenter)

        self.setObjectName("StatCard")
        self.setStyleSheet("""
            QFrame#StatCard {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel { color: #2b2b2b; }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title, alignment=Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #fff;")
        self._display_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #4c8caf;")

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

        configure_matplotlib()

        # --- Banner + Stats ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        main_layout.addLayout(top_layout)

        if image_path:
            self.banner = QLabel(alignment=Qt.AlignCenter)
            self.banner.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            top_layout.addWidget(self.banner)
            self.update_banner()

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout.addWidget(stats_widget)

        self.cards = {
            "total": StatCard("Total Notes"),
            "cats": StatCard("Categories"),
            "monthly": StatCard("Notes This Month"),
        }
        for c in self.cards.values():
            c.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            stats_layout.addWidget(c)

        # --- Charts ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)
        charts_widget = QWidget()
        charts_widget.setLayout(charts_layout)
        charts_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(charts_widget, stretch=3)

        self.line_figure = Figure(figsize=(5, 4), dpi=100)
        self.line_canvas = FigureCanvas(self.line_figure)
        self.line_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.line_canvas)

        self.heatmap_figure = Figure(figsize=(5, 4), dpi=100)
        self.heatmap_canvas = FigureCanvas(self.heatmap_figure)
        self.heatmap_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.heatmap_canvas)

        # --- Recent Note + Timezone Clock Side-by-Side ---
        recent_tz_layout = QHBoxLayout()
        recent_tz_layout.setSpacing(12)

        # Left: Recent notes
        self.recent_view = RecentNoteView(self.model, self.open_note_callback)
        recent_tz_layout.addWidget(self.recent_view, stretch=3)

        # Right: Timezone clock with title
        tz_layout = QVBoxLayout()
        tz_layout.setSpacing(6)

        tz_title = QLabel("Timezones", alignment=Qt.AlignCenter)
        tz_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #fff;")
        tz_layout.addWidget(tz_title)

        self.timezone_clock = TimezoneClock()
        tz_layout.addWidget(self.timezone_clock, stretch=1)

        tz_widget = QWidget()
        tz_widget.setLayout(tz_layout)
        tz_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        recent_tz_layout.addWidget(tz_widget, stretch=1)

        # Wrap both sides in a widget
        recent_tz_widget = QWidget()
        recent_tz_widget.setLayout(recent_tz_layout)
        main_layout.addWidget(recent_tz_widget, stretch=2)

        # Initial data
        self.refresh_dashboard()
        self.load_stylesheet()

    # --- Stats ---
    def update_stats(self, animated=True):
        values = calculate_stats(self.model)
        for key, val in values.items():
            card = self.cards[key]
            if animated:
                self.animate_card_value(card, val)
            else:
                card._set_value(val)

    def animate_card_value(self, card, new_value):
        anim = QPropertyAnimation(card, b"value", self)
        anim.setDuration(800)
        anim.setStartValue(card.value)
        anim.setEndValue(new_value)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        card._anim = anim

    # --- Graphs ---
    def update_graphs(self):
        self.update_line_chart()
        self.update_heatmap()

    # --- Refresh everything ---
    def refresh_dashboard(self):
        """Update stats and graphs automatically."""
        self.update_stats(animated=True)
        self.update_graphs()

    def update_line_chart(self):
        self.line_figure.clear()
        ax = self.line_figure.add_subplot(111)
        ax.set_facecolor("#2b2b2b")
        self.line_figure.patch.set_facecolor("#2b2b2b")

        categories = self.model.get_all_categories()
        all_dates = sorted({datetime.fromisoformat(n["created"]).date() for c in categories for n in self.model.get_notes(category_name=c)})
        if not all_dates:
            return

        x = list(range(len(all_dates)))
        colors = ['#4c8caf', '#c24cfa', '#4cfa8c', '#fa4c4c', '#ffa500']

        for i, cat in enumerate(categories):
            notes = self.model.get_notes(category_name=cat)
            cumulative = 0
            y = []
            for d in all_dates:
                count = sum(1 for n in notes if datetime.fromisoformat(n["created"]).date() == d)
                cumulative += count
                y.append(cumulative)
            ax.plot(x, y, color=colors[i % len(colors)], linewidth=2,
                    marker='o', markersize=6, label=cat)

        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime("%b %d") for d in all_dates], rotation=45, color="#e0e0e0")
        ax.set_ylabel("Total Notes", color="#e0e0e0")
        ax.set_title("Cumulative Notes by Category", color="#e0e0e0")
        ax.tick_params(colors="#e0e0e0")
        ax.legend(facecolor="#2b2b2b", edgecolor="#4c8caf", labelcolor="#e0e0e0")

        self.line_canvas.draw()

    def update_heatmap(self):
        self.heatmap_figure.clear()
        ax = self.heatmap_figure.add_subplot(111)
        ax.set_facecolor("#2b2b2b")
        self.heatmap_figure.patch.set_facecolor("#2b2b2b")

        categories = self.model.get_all_categories()
        all_dates = sorted({datetime.fromisoformat(n["created"]).date() for c in categories for n in self.model.get_notes(category_name=c)})
        if not all_dates:
            return

        heat_data = []
        for cat in categories:
            notes = self.model.get_notes(category_name=cat)
            y = []
            for d in all_dates:
                lengths = [len(n["content"]) for n in notes if datetime.fromisoformat(n["created"]).date() == d]
                y.append(np.mean(lengths) if lengths else 0)
            heat_data.append(y)

        im = ax.imshow(heat_data, aspect='auto', cmap='viridis', origin='lower')
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories, color="#e0e0e0")
        ax.set_xticks([])
        ax.set_title("Average Note Length per Category by Date", color="#e0e0e0")
        self.heatmap_figure.colorbar(im, ax=ax)
        self.heatmap_canvas.draw()

    # --- Banner ---
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            print(f"Failed to load banner image: {self.image_path}")
            return
        max_width = 200
        max_height = self.height() // 2
        scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.banner.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "banner"):
            self.update_banner()

    def open_note_callback(self, note):
        self.parent().open_editor(note["id"])

    # --- Stylesheet ---
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/dark_theme.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load dark_theme.qss:", e)
