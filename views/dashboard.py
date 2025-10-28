import os
import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap

import matplotlib

# Force QtAgg backend for PySide6
matplotlib.use("QtAgg")

# Fix datapath for PyInstaller
try:
    # If running in a PyInstaller bundle, _MEIPASS is the temp folder
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    mpl_data_path = os.path.join(base_path, "mpl-data")
    if os.path.exists(mpl_data_path):
        matplotlib.rcParams["datapath"] = mpl_data_path
        print(f"[Matplotlib] datapath set to: {mpl_data_path}")
    else:
        print("[Matplotlib] mpl-data folder not found, using default.")
except Exception as e:
    print(f"[Matplotlib] configuration skipped: {e}")

# Import FigureCanvas after backend is set
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datetime import datetime
from utils.resource_path import resource_path, configure_matplotlib
from views.news_feed import NewsFeedView
import numpy as np

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

        configure_matplotlib()

        # --- Banner + Stats in Horizontal Layout ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        main_layout.addLayout(top_layout)

        if image_path:
            self.banner = QLabel()
            self.banner.setAlignment(Qt.AlignCenter)
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

        # --- Charts Layout ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)
        charts_widget = QWidget()
        charts_widget.setLayout(charts_layout)
        charts_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(charts_widget, stretch=3)

        # Line Chart
        self.line_figure = Figure(figsize=(5, 4), dpi=100)
        self.line_canvas = FigureCanvas(self.line_figure)
        self.line_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.line_canvas)

        # Heatmap (Note Length by Category and Date)
        self.heatmap_figure = Figure(figsize=(5, 4), dpi=100)
        self.heatmap_canvas = FigureCanvas(self.heatmap_figure)
        self.heatmap_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.heatmap_canvas)

        # --- News Feed ---
        self.news_feed = NewsFeedView(
            feed_url=""
        )
        self.news_feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.news_feed, stretch=2)

        # Initial data
        self.update_stats(animated=False)
        self.update_graphs()
        self.load_stylesheet()

    # --- Stats ---
    def update_stats(self, animated=True):
        categories = self.model.get_all_categories()
        all_notes = []
        for c in categories:
            all_notes.extend(self.model.get_notes(category_name=c))

        total = len(all_notes)
        monthly_count = sum(1 for n in all_notes if datetime.fromisoformat(n["created"]).month == datetime.now().month)
        cats = len(categories)

        values = {
            "total": total,
            "cats": cats,
            "monthly": monthly_count,
        }

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

            # Add markers to show points
            ax.plot(x, y,
                    color=colors[i % len(colors)],
                    linewidth=2,
                    marker='o',  # <-- marker added
                    markersize=6,  # size of each point
                    label=cat)

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
        #ax.set_xticks(range(len(all_dates)))
        #ax.set_xticklabels([d.strftime("%b %d") for d in all_dates], rotation=45, color="#e0e0e0", ha='right')
        ax.set_title("Average Note Length per Category by Date", color="#e0e0e0")
        self.heatmap_figure.colorbar(im, ax=ax)
        self.heatmap_canvas.draw()

    # --- Banner ---
    def update_banner(self):
        if not self.image_path:
            return
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            print(f"⚠️ Failed to load banner image: {self.image_path}")
            return
        max_width = 200  # fixed width for left-side banner
        max_height = self.height() // 2
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

    # --- Stylesheet ---
    def load_stylesheet(self):
        try:
            with open(resource_path("ui/themes/dark.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load dark.qss:", e)
