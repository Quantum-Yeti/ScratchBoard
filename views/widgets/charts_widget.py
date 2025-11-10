from datetime import datetime, timedelta
from PySide6.QtCharts import QChart, QChartView, QSplineSeries, QLineSeries, QBarSet, QBarSeries, QValueAxis, QCategoryAxis
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

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



def create_multi_line_chart(model, months_back=3):
    """
    Multi-line chart showing number of notes added per category per month.
    - months_back: how many past months to include
    """
    chart = QChart()
    chart.setAnimationOptions(QChart.AllAnimations)
    chart.setBackgroundVisible(False)

    # --- Generate month keys ---
    now = datetime.now()
    months = []
    for i in reversed(range(months_back)):
        m = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        months.append(m.strftime("%Y-%m"))

    categories = model.get_all_categories()
    overall_max = 0
    series_list = []

    # --- Create series for each category ---
    for cat in categories:
        notes = model.get_notes(category_name=cat)
        if not notes:
            continue

        # Count notes per month
        notes_by_month = {}
        for n in notes:
            date_key = datetime.fromisoformat(n["created"]).strftime("%Y-%m")
            notes_by_month[date_key] = notes_by_month.get(date_key, 0) + 1

        # Build series with at least 2 points
        series = QSplineSeries()
        series.setName(cat)
        series.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))

        points = [(i, notes_by_month.get(month, 0)) for i, month in enumerate(months)]
        if len(points) == 1:
            points.append((1, points[0][1]))  # duplicate single point

        for x, y in points:
            overall_max = max(overall_max, y)
            series.append(x, y)

        chart.addSeries(series)
        series_list.append(series)

    if not series_list:
        return chart  # no data

    # --- X Axis ---
    axis_x = QCategoryAxis()
    for i, month in enumerate(months):
        axis_x.append(month, i)
    axis_x.setLabelsColor(QColor("white"))
    axis_x.setLineVisible(False)
    axis_x.setGridLineVisible(False)
    chart.addAxis(axis_x, Qt.AlignBottom)

    # --- Y Axis ---
    axis_y = QValueAxis()
    axis_y.setRange(0, overall_max + 1)
    axis_y.setLabelFormat("%d")
    axis_y.setLabelsColor(QColor("white"))
    axis_y.setLineVisible(False)
    axis_y.setGridLineVisible(False)
    axis_y.setVisible(False)
    chart.addAxis(axis_y, Qt.AlignLeft)

    # --- Attach axes ---
    for s in series_list:
        s.attachAxis(axis_x)
        s.attachAxis(axis_y)

    # --- Styling ---
    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Notes Added per Category per Month")
    chart.setTitleBrush(QColor("white"))

    return chart

