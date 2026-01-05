import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCharts import QChart, QSplineSeries, QValueAxis, \
    QCategoryAxis
from PySide6.QtGui import QColor, QFont, QIcon, QCursor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QSizePolicy, QMessageBox, QToolTip

from helpers.ui_helpers.chart_pastel_list import PASTEL_CHART_COLORS
from domain.analytics.dashboard_stats import calculate_stats
from ui.menus.context_menu import ModifyContextMenu
from ui.themes.dash_action_btn_style import dash_action_button_style
from ui.themes.scrollbar_style import vertical_scrollbar_style
from utils.custom_q_edit import CustomQEdit
from utils.resource_path import resource_path
from views.widgets.arm_pop_widget import open_arm_pop
from views.widgets.db_stats_pop import update_db_stats

# Set font for dashboard stats
segoe = QFont("Segoe UI", 11)

### --- Apply Tooltip Style Override --- ###
def apply_tooltip_style(widget):
    widget.setStyleSheet(widget.styleSheet() + """
    QToolTip {
        background-color: #222;
        color: #eee;
        border: 1px solid #555;
        padding: 6px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    """)

# Subclass CustomQEdit just to override the context menu
class ArmTextEdit(CustomQEdit, ModifyContextMenu):
    def contextMenuEvent(self, event):
        ModifyContextMenu.contextMenuEvent(self, event)


### --- Stacked bar chart --- ###
def dashboard_left_panel(model):
    """
    Create the left-side dashboard panel.

    Provides an editable ARM statement area with save and pop-out actions,
    along with quick-access buttons for database statistics and email.
    The returned widget exposes update hooks for dynamic refresh.

    Args:
        model (NoteModel): Data model used for database statistics.

    Returns:
        QWidget: A configured dashboard panel widget.
    """
    panel = QWidget()
    panel.setStyleSheet("background-color: #2C2C2C;")
    apply_tooltip_style(panel)
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    layout = QVBoxLayout(panel)
    layout.setSpacing(8)
    layout.setContentsMargins(0, 0, 0, 0)

    arm_text = ArmTextEdit()
    arm_text.verticalScrollBar().setStyleSheet(vertical_scrollbar_style)
    arm_text.setPlaceholderText("Type your ARM statement (or a quick note) here then click save; it auto-loads after saving.")
    arm_text.setStyleSheet(f"""
        QTextEdit {{
            padding: 10px;   
        }}
        QScrollBar:vertical {{
            {vertical_scrollbar_style}
        }}
    """)
    layout.addWidget(arm_text, stretch=1)

    # Horizontal layout for buttons
    button_layout = QHBoxLayout()
    button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    button_layout.setContentsMargins(0, 0, 0, 5)

    save_icon = QIcon(resource_path("resources/icons/save_arm.png"))
    save_btn = QPushButton("Save Arm")
    save_btn.setToolTip("Save your ARM statement (or a quick note).")
    save_btn.setStyleSheet(dash_action_button_style)
    save_btn.setIcon(save_icon)
    apply_tooltip_style(save_btn)

    pop_icon = QIcon(resource_path("resources/icons/pop_arm.png"))
    pop_btn = QPushButton("Pop Arm")
    pop_btn.setToolTip("Pop your ARM statement open.")
    pop_btn.setStyleSheet(dash_action_button_style)
    pop_btn.setIcon(pop_icon)
    apply_tooltip_style(pop_btn)
    pop_btn.clicked.connect(open_arm_pop)

    db_btn_icon = QIcon(resource_path("resources/icons/db_pop.png"))
    db_stats_btn = QPushButton("DB Stats")
    db_stats_btn.setToolTip("Check your database stats.")
    db_stats_btn.setStyleSheet(dash_action_button_style)
    db_stats_btn.setIcon(db_btn_icon)
    apply_tooltip_style(db_stats_btn)
    db_stats_btn.clicked.connect(lambda: update_db_stats(model))

    email_btn_icon = QIcon(resource_path("resources/icons/email_pop.png"))
    email_btn = QPushButton("Email")
    email_btn.setToolTip("Check your email.")
    email_btn.setStyleSheet(dash_action_button_style)
    email_btn.setIcon(email_btn_icon)
    apply_tooltip_style(email_btn)
    email_btn.clicked.connect(lambda: webbrowser.open("https://outlook.com"))

    # Add buttons to button layout
    button_layout.addWidget(save_btn)
    button_layout.addWidget(pop_btn)
    button_layout.addWidget(db_stats_btn)
    button_layout.addWidget(email_btn)

    # Set mouse cursor shape for buttons
    def set_btn_cursor(*buttons: QPushButton):
        for btn in buttons:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

    set_btn_cursor(
        save_btn,
        pop_btn,
        db_stats_btn,
        email_btn
    )

    # Add button layout to main layout
    layout.addLayout(button_layout)

    def save_arm_statement():
        try:
            Path("sb_data/notepad").mkdir(exist_ok=True)
            with open("sb_data/notepad/arm_statement.txt", "w", encoding="utf-8") as s:
                s.write(arm_text.toPlainText())

            # Success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText("ARM statement saved successfully!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except Exception as e:
            # Error message if something goes wrong
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to save ARM statement: {str(e)}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    save_btn.clicked.connect(save_arm_statement)

    # Load existing ARM statement
    try:
        with open("sb_data/notepad/arm_statement.txt", "r", encoding="utf-8") as f:
            arm_text.setPlainText(f.read())
    except FileNotFoundError:
        pass

    # Attach update methods so DashboardView can refresh dynamically
    panel.update_db_stats = update_db_stats

    # Return the left panel layout and buttons
    return panel

###--- Multi-line chart ---###
def create_multi_line_chart(model, days_back=14):
    """
    Build a multi-line time-series chart of daily model statistics.

    The chart plots selected statistics (e.g., contacts and reference links)
    for each day in the past `days_back` range. Values are recalculated per day
    by temporarily overriding the model's target date.

    Args:
        model (NoteModel): Data model used to compute daily statistics.
        days_back (int): Number of past days to include in the chart.

    Returns:
        QChart: A styled Qt chart with one line per statistic, a hidden date
        axis, dynamic Y-axis scaling, and an auto-generated legend.
    """
    chart = QChart()
    chart.setFont(segoe)
    chart.setTitleFont(QFont("Segoe UI", 12))
    chart.legend().setFont(segoe)
    chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
    chart.setBackgroundVisible(False)
    chart.setTitle("Activity Trends")
    chart.setTitleBrush(QColor("white"))

    # Time range
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)) for i in reversed(range(days_back))]

    # Stats to plot
    stat_keys = [
        #("daily_notes", "Daily Notes"),
        #("daily_words", "Daily Words"),
        #("rolling_notes", "Avg Notes/Day"),
        ("rolling_words", "Avg Words/Day"),
        #("total_ratio", "Note Ratio"),
        ("cumulative_wave", "Words/Week"),
        #("category_entropy_norm", "Balance"),
        ("contacts", "Contacts"),
        ("links", "Links")
    ]

    # Precompute stats for each day from the model
    daily_stats = []
    for d in dates:
        model.override_date_for_stats = d
        stats = calculate_stats(model)
        daily_stats.append(stats)

    # Generate a series for each stat
    max_value = 0
    min_value = float("inf")
    for idx, (key, name) in enumerate(stat_keys):
        series = QSplineSeries()
        series.setName(name)
        series.setUseOpenGL(True)

        # Apply curated color palette
        color = QColor(PASTEL_CHART_COLORS[idx % len(PASTEL_CHART_COLORS)])
        series.setColor(color)

        # Line thickness
        pen = series.pen()
        pen.setWidth(2)
        pen.setColor(color)
        series.setPen(pen)

        for i, stats in enumerate(daily_stats):
            val = int(round(stats.get(key, 0))) # round to a whole number
            series.append(i, val)
            max_value = max(max_value, val)
            min_value = min(min_value, val)

        def create_tooltip(series_name=name):
            def show_tooltip(point, state):
                if state:  # mouse over
                    QToolTip.showText(
                        QCursor.pos(),
                        f"{series_name}\nValue: {int(round(point.y()))}\nDay: {dates[int(point.x())].strftime('%b %d')}"
                    )
                else:
                    QToolTip.hideText()
            return show_tooltip

        series.hovered.connect(create_tooltip())

        chart.addSeries(series)

        # Legend styling
        chart.legend().setVisible(True)
        chart.legend().setLabelColor(QColor("white"))

    # X axis (dates)
    axis_x = QCategoryAxis()
    axis_x.setGridLineVisible(False)
    axis_x.setVisible(False)
    for i, d in enumerate(dates):
        if i % 5 == 0:   # fewer labels
            axis_x.append(d.strftime("%b %d"), i)
    axis_x.setLabelsColor(QColor("white"))
    chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

    # Y axis
    axis_y = QValueAxis()

    # Compute min and max of all stats
    all_values = [stats.get(key, 0) for stats in daily_stats for key, _ in stat_keys]
    min_val = min(all_values, default=0)
    max_val = max(all_values, default=1)
    # Add padding to axis y
    padding = (max_val - min_val) * 0.3 # maximum - minimum * percent to padd
    axis_y.setRange(min_val - padding, max_val + padding)

    #axis_y.setRange(-3, max_value + 1) # Will leave for now
    axis_y.setLabelFormat("%d")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setVisible(False)
    chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

    # Starts the y-axis at a minimum of -1 to prevent lines visually dipping below 0
    #axis_y.setMin(-1) # Will leave for now

    # Attach axes
    for s in chart.series():
        s.attachAxis(axis_x)
        s.attachAxis(axis_y)

    # Legend
    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))

    # Makes the legend marker outlines more pronounced
    for marker in chart.legend().markers():
        pen = marker.pen()
        pen.setWidth(1)
        marker.setPen(pen)

        brush = marker.brush()
        marker.setBrush(brush)

    return chart