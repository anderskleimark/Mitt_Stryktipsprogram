from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget
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

        layout = self.create_layout()

        layout.addWidget(
            self.create_header("Lägg till en kupong")
        )

        layout.addSpacing(25)
        self.year_week_widget = YearWeekWidget()

        layout.addWidget(
            self.year_week_widget
        )

        # Matchtabell
        self.matches_table = QTableWidget(13, 2)

        self.matches_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag"]
        )

        self.matches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        for row in range(13):
            self.matches_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        layout.addWidget(self.matches_table)

        # Knappar
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Spara kupong")
        self.clear_button = QPushButton("Rensa")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_matches(self):
        matches = []

        for row in range(self.matches_table.rowCount()):
            home_item = self.matches_table.item(row, 0)
            away_item = self.matches_table.item(row, 1)

            home = home_item.text().strip() if home_item else ""
            away = away_item.text().strip() if away_item else ""

            matches.append((row + 1, home, away))

        return matches

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.year_week_widget.reset()
        for row in range(self.matches_table.rowCount()):
            for col in range(self.matches_table.columnCount()):
                item = self.matches_table.item(row, col)
                if item:
                    item.setText("")
