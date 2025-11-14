from datetime import datetime, timedelta
from PySide6.QtCharts import QChart, QChartView, QSplineSeries, QLineSeries, QBarSet, QBarSeries, QValueAxis, \
    QCategoryAxis, QLegendMarker
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from helpers.chart_pastel_list import PASTEL_CHART_COLORS
from helpers.dashboard_stats import calculate_stats

# Stacked bar chart
def create_stacked_bar_chart(model):
    chart = QChart()
    chart.setAnimationOptions(QChart.SeriesAnimations)
    chart.setBackgroundVisible(False)

    categories = model.get_all_categories()

    # All unique dates
    all_dates = sorted({
        datetime.fromisoformat(n["created"]).date()
        for cat in categories
        for n in model.get_notes(category_name=cat)
    })

    if not all_dates:
        return chart

    bar_series = QBarSeries()
    overall_max = 0

    for cat in categories:
        notes = model.get_notes(category_name=cat)
        notes_by_date = {}
        for n in notes:
            d = datetime.fromisoformat(n["created"]).date()
            notes_by_date[d] = notes_by_date.get(d, 0) + 1

        values = [notes_by_date.get(d, 0) for d in all_dates]
        overall_max = max(overall_max, max(values, default=0))

        bar_set = QBarSet(cat)
        bar_set.append(values)
        bar_set.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))
        bar_series.append(bar_set)

    chart.addSeries(bar_series)

    # X axis
    axis_x = QCategoryAxis()
    for i, d in enumerate(all_dates):
        axis_x.append(d.strftime("%b %d"), i)
    axis_x.setLabelsColor(QColor("white"))
    axis_x.setLineVisible(False)
    axis_x.setGridLineVisible(False)
    chart.addAxis(axis_x, Qt.AlignBottom)

    # Y-axis with explicit range
    axis_y = QValueAxis()
    axis_y.setTitleText("Notes Added")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setVisible(False)
    axis_y.setLabelFormat("%d")
    axis_y.setRange(0, overall_max + 1)
    chart.addAxis(axis_y, Qt.AlignLeft)

    # Attach axes
    bar_series.attachAxis(axis_x)
    bar_series.attachAxis(axis_y)

    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Notes Added per Day by Category")
    chart.setTitleBrush(QColor("white"))

    return chart

# Multi-line chart
def create_multi_line_chart(model, days_back=30):
    """
    Multi-line chart showing dashboard stats over time.
    The stats come from calculate_stats(model), ensuring the
    graph matches the dashboard's stat cards.
    """

    chart = QChart()
    chart.setAnimationOptions(QChart.AllAnimations)
    chart.setBackgroundVisible(False)
    chart.setTitle("Note Activity Trends (Past 30 Days)")
    chart.setTitleBrush(QColor("white"))

    # Time range
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)) for i in reversed(range(days_back))]

    # Stats to plot
    stat_keys = [
        ("total",         "Total Notes"),
        ("monthly",       "Notes This Month"),
        ("today",         "Notes Today"),
        ("avg_words",     "Avg Words/Note"),
        ("longest_note",  "Longest Note"),
        ("shortest_note", "Shortest Note"),
    ]

    # Precompute stats for each day from the model
    daily_stats = []
    for d in dates:
        model.override_date_for_stats = d
        stats = calculate_stats(model)
        daily_stats.append(stats)

    # Generate a series for each stat
    max_value = 0
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
            val = stats.get(key, 0)
            max_value = max(max_value, val)
            series.append(i, val)

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
    chart.addAxis(axis_x, Qt.AlignBottom)

    # Y axis
    axis_y = QValueAxis()
    axis_y.setRange(0, max_value + 2)
    axis_y.setLabelFormat("%d")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setVisible(False)
    chart.addAxis(axis_y, Qt.AlignLeft)

    # Starts the y-axis at a minimum of -1 to prevent lines visually dipping below 0
    axis_y.setMin(-1)

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

