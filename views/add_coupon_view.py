from mvc import Model, View, Controller
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton
)
from datetime import datetime


class AddCouponView(View):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Lägg till en kupong")
        header.setFont(self.header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # År och vecka
        now = datetime.now()
        form_widget = QWidget()
        form_layout = QGridLayout()

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(2000, 2100)

        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, 53)

        self.year_spinbox.setValue(now.isocalendar().year)
        self.week_spinbox.setValue(now.isocalendar().week)

        form_layout.addWidget(QLabel("År"), 0, 0)
        form_layout.addWidget(self.year_spinbox, 0, 1)

        form_layout.addWidget(QLabel("Vecka"), 0, 2)
        form_layout.addWidget(self.week_spinbox, 0, 3)

        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        # Matchtabell
        self.matches_table = QTableWidget(13, 2)

        self.matches_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag"]
        )

        self.matches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Matchnummer som radrubriker
        for row in range(13):
            self.matches_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        layout.addWidget(self.matches_table)

        # Knappar (Spara + Rensa)
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Spara kupong")
        self.clear_button = QPushButton("Rensa")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_year(self):
        return self.year_spinbox.value()

    def get_week(self):
        return self.week_spinbox.value()

    def get_matches(self):
        matches = []

        for row in range(self.matches_table.rowCount()):
            home_item = self.matches_table.item(row, 0)
            away_item = self.matches_table.item(row, 1)

            home = home_item.text().strip() if home_item else ""
            away = away_item.text().strip() if away_item else ""

            matches.append((row + 1, home, away))

        return matches

    def update(self, model):
        pass

    def clear_form(self):
        now = datetime.now()
        # Rensa år och vecka
        self.year_spinbox.setValue(now.isocalendar().year)
        self.week_spinbox.setValue(now.isocalendar().week)

        for row in range(self.matches_table.rowCount()):
            for col in range(self.matches_table.columnCount()):
                item = self.matches_table.item(row, col)
                if item:
                    item.setText("")
