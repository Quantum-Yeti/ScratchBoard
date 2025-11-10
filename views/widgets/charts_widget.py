from datetime import datetime
from PySide6.QtCharts import QChart, QChartView, QSplineSeries, QLineSeries, QBarSet, QBarSeries, QValueAxis, QCategoryAxis
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

def create_stacked_bar_chart(model):
    chart = QChart()
    chart.setAnimationOptions(QChart.SeriesAnimations)
    chart.setBackgroundVisible(False)

    categories = model.get_all_categories()
    all_dates = sorted({datetime.fromisoformat(n["created"]).date()
                        for c in categories
                        for n in model.get_notes(category_name=c)})

    if not all_dates:
        return chart

    bar_series = QBarSeries()
    for cat in categories:
        notes = model.get_notes(category_name=cat)
        notes_by_date = {}
        for n in notes:
            d = datetime.fromisoformat(n["created"]).date()
            notes_by_date[d] = notes_by_date.get(d, 0) + 1

        bar_set = QBarSet(cat)
        bar_set.append([notes_by_date.get(d, 0) for d in all_dates])
        bar_set.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))
        bar_series.append(bar_set)

    chart.addSeries(bar_series)

    axis_x = QCategoryAxis()
    for i, d in enumerate(all_dates):
        axis_x.append(d.strftime("%b %d"), i)
    axis_x.setLabelsColor(QColor("white"))
    axis_x.setLineVisible(False)
    axis_x.setGridLineVisible(False)
    chart.addAxis(axis_x, Qt.AlignBottom)

    axis_y = QValueAxis()
    axis_y.setTitleText("Notes Added")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setLabelFormat("%d")
    chart.addAxis(axis_y, Qt.AlignLeft)

    bar_series.attachAxis(axis_x)
    bar_series.attachAxis(axis_y)

    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Notes Added per Day by Category")
    chart.setTitleBrush(QColor("white"))

    return chart


def create_multi_line_chart(model, buffer_ratio=0.1, bottom_buffer_ratio=0.05):
    """
    Multi-line chart showing number of words added per category per day.
    Adds a small top and bottom buffer to keep lines fully inside chart.
    """
    chart = QChart()
    chart.setAnimationOptions(QChart.AllAnimations)
    chart.setBackgroundVisible(False)

    categories = model.get_all_categories()
    all_dates = sorted({
        datetime.fromisoformat(n["created"]).date()
        for c in categories
        for n in model.get_notes(category_name=c)
    })

    if not all_dates:
        return chart

    series_list = []
    overall_max = 0

    # --- Create series ---
    for cat in categories:
        notes = model.get_notes(category_name=cat)
        words_by_date = {}
        for n in notes:
            d = datetime.fromisoformat(n["created"]).date()
            word_count = len(n["content"].split())
            words_by_date[d] = words_by_date.get(d, 0) + word_count

        max_value = max(words_by_date.values(), default=0)
        overall_max = max(overall_max, max_value)

        series = QSplineSeries()
        series.setName(cat)
        series.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))

        for i, date in enumerate(all_dates):
            # Clip to bottom buffer to prevent dipping below axis
            value = max(0, words_by_date.get(date, 0))
            series.append(i, value)

        series_list.append(series)
        chart.addSeries(series)

    # --- X Axis ---
    axis_x = QCategoryAxis()
    for i, date in enumerate(all_dates):
        axis_x.append(date.strftime("%b %d"), i)
    axis_x.setLabelsColor(QColor("white"))
    axis_x.setLineVisible(False)
    axis_x.setGridLineVisible(False)
    axis_x.setVisible(False)
    chart.addAxis(axis_x, Qt.AlignBottom)

    # --- Y Axis with top and bottom buffer ---
    top_buffer = max(1, int(overall_max * buffer_ratio))
    bottom_buffer = -2 # set to >= -1 otherwise the lines will go below the graph boundary visually, super annoying

    axis_y = QValueAxis()
    axis_y.setTitleText("Words Added")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setVisible(False)
    axis_y.setRange(bottom_buffer, overall_max + top_buffer)
    axis_y.setLabelFormat("%d")
    axis_y.setTickCount(overall_max + top_buffer + 1)
    chart.addAxis(axis_y, Qt.AlignLeft)

    # --- Attach axes ---
    for s in series_list:
        s.attachAxis(axis_x)
        s.attachAxis(axis_y)

    # --- Styling ---
    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Words Added per Day by Category")
    chart.setTitleBrush(QColor("white"))

    return chart
