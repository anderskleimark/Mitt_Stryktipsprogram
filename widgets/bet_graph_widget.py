from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                              QChartView, QValueAxis)
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame

from widgets.base_widget import BaseWidget


class BetGraphWidget(BaseWidget):
    # Konstanter
    LAYOUT_SPACING = 12

    def __init__(self):
        super().__init__()
        self._build_widget()

    def _build_widget(self):
        layout = self.create_vertical_layout(
            parent=self,
            spacing=self.LAYOUT_SPACING
        )

        self.chart_view = QChartView()
        self.chart_view.setFrameShape(QFrame.Shape.NoFrame)

        self.chart_view.setStyleSheet("""
            QChartView {
                background-color: white;
                border: none;
            }
        """)

        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self.chart_view.setAutoFillBackground(True)
        layout.addWidget(self.chart_view)

    def copy_diagram_to_clipboard(self):
        """
            Kopierar diagrammet till urklipp.
        """
        chart = self.chart_view.chart()

        pixmap = QPixmap(self.chart_view.size())
        pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(pixmap)

        chart.scene().render(painter)

        painter.end()
        QGuiApplication.clipboard().setPixmap(pixmap)

    def save_diagram_as_image(self):
        """
            Sparar diagrammet som bild.
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Spara diagram",
            "diagram.png",
            (
                "PNG-bilder (*.png);;"
                "JPEG-bilder (*.jpg *.jpeg)"
            )
        )

        if not filename:
            return

        pixmap = self.chart_view.grab()
        pixmap.save(filename)

    def update_statistic_graph(
        self,
        data,
        average
    ):
        """
        Uppdaterar diagrammet med statistik
        över antal rätt.
        """
        series = QBarSeries()

        bar_set = QBarSet("Antal rätt")

        categories = []
        max_value = 0

        for item in data:
            correct = str(item["ratt"])

            count = item["antal"]
            categories.append(correct)
            bar_set.append(count)

            max_value = max(
                max_value,
                count
            )

        series.append(bar_set)
        chart = QChart()

        chart.addSeries(series)

        chart.setTitle(
            (
                "Frekvens av antal rätt – "
                f"Genomsnitt: {average:.2f} rätt"
            )
        )

        chart.setTheme(
            QChart.ChartTheme.ChartThemeLight
        )

        chart.setMargins(
            QMargins(
                25,
                25,
                25,
                25
            )
        )

        chart.layout().setContentsMargins(
            20,
            10,
            20,
            20
        )

        chart.setBackgroundBrush(Qt.GlobalColor.white)
        chart.setPlotAreaBackgroundBrush(Qt.GlobalColor.white)
        chart.setBackgroundVisible(True)
        chart.setPlotAreaBackgroundVisible(True)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)

        axis_x.setLabelsBrush(Qt.GlobalColor.black)
        axis_x.setGridLineVisible(False)

        chart.addAxis(
            axis_x,
            Qt.AlignmentFlag.AlignBottom
        )

        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")

        axis_y.setRange(
            0,
            max(
                1,
                max_value
            )
        )

        axis_y.setTickCount(
            max(
                2,
                max_value + 1
            )
        )

        axis_y.setLabelsBrush(Qt.GlobalColor.black)
        axis_y.setGridLineColor(Qt.GlobalColor.lightGray)

        chart.addAxis(
            axis_y,
            Qt.AlignmentFlag.AlignLeft
        )

        series.attachAxis(axis_y)

        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_view.setChart(chart)
