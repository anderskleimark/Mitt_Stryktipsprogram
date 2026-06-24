from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QSpinBox
)


class YearWeekWidget(QWidget):

    def __init__(self):
        super().__init__()

        now = datetime.now()

        layout = QHBoxLayout()

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(2000, 2100)
        self.year_spinbox.setValue(
            now.isocalendar().year
        )

        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, 53)
        self.week_spinbox.setValue(
            now.isocalendar().week
        )

        layout.addWidget(QLabel("År"))
        layout.addWidget(self.year_spinbox)

        layout.addSpacing(20)

        layout.addWidget(QLabel("Vecka"))
        layout.addWidget(self.week_spinbox)

        layout.addStretch()

        self.setLayout(layout)

    def get_year(self):
        return self.year_spinbox.value()

    def get_week(self):
        return self.week_spinbox.value()

    def reset(self):
        now = datetime.now()

        self.year_spinbox.setValue(
            now.isocalendar().year
        )

        self.week_spinbox.setValue(
            now.isocalendar().week
        )
