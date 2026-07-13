from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QWidget


class YearWeekWidget(QWidget):

    year_week_changed = Signal(int, int)

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

        layout.addWidget(QLabel("Omgång"))
        layout.addWidget(self.week_spinbox)

        layout.addStretch()

        self.setLayout(layout)

        # Koppla signaler
        self.year_spinbox.valueChanged.connect(self._emit_year_week_changed)
        self.week_spinbox.valueChanged.connect(self._emit_year_week_changed)

    def _emit_year_week_changed(self):
        self.year_week_changed.emit(
            self.get_year(),
            self.get_week()
        )

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

    def set_active_status(self, status):
        self.year_spinbox.setEnabled(status)
        self.week_spinbox.setEnabled(status)
