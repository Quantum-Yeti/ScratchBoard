from datetime import datetime
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QBarSet, QBarSeries, QValueAxis, QCategoryAxis
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
    chart.addAxis(axis_x, Qt.AlignBottom)

    axis_y = QValueAxis()
    axis_y.setTitleText("Notes Added")
    axis_y.setLabelsColor(QColor("white"))
    chart.addAxis(axis_y, Qt.AlignLeft)

    bar_series.attachAxis(axis_x)
    bar_series.attachAxis(axis_y)

    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Notes Added per Day by Category")
    chart.setTitleBrush(QColor("white"))

    return chart


def create_multi_line_chart(model):
    chart = QChart()
    chart.setAnimationOptions(QChart.AllAnimations)
    chart.setBackgroundVisible(False)

    categories = model.get_all_categories()
    all_dates = sorted({datetime.fromisoformat(n["created"]).date()
                        for c in categories
                        for n in model.get_notes(category_name=c)})
    if not all_dates:
        return chart

    for cat in categories:
        notes = model.get_notes(category_name=cat)
        notes_by_date = {}
        for n in notes:
            d = datetime.fromisoformat(n["created"]).date()
            notes_by_date[d] = notes_by_date.get(d, 0) + 1

        series = QLineSeries()
        series.setName(cat)
        series.setColor(QColor.fromHsv(hash(cat) % 360, 255, 200))

        for i, date in enumerate(all_dates):
            series.append(i, notes_by_date.get(date, 0))

        chart.addSeries(series)

    axis_x = QCategoryAxis()
    for i, date in enumerate(all_dates):
        axis_x.append(date.strftime("%b %d"), i)
    axis_x.setLabelsColor(QColor("white"))
    chart.addAxis(axis_x, Qt.AlignBottom)

    axis_y = QValueAxis()
    axis_y.setTitleText("Notes Added")
    axis_y.setLabelsColor(QColor("white"))
    chart.addAxis(axis_y, Qt.AlignLeft)

    for s in chart.series():
        s.attachAxis(axis_x)
        s.attachAxis(axis_y)

    chart.legend().setVisible(True)
    chart.legend().setLabelColor(QColor("white"))
    chart.setTitle("Notes Added per Day by Category")
    chart.setTitleBrush(QColor("white"))

    return chart
