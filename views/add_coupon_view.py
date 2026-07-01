from mvc import Model, View, Controller
from models.coupon_model import Game
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
        self.game_table = QTableWidget(13, 2)

        self.game_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag"]
        )

        self.game_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        for row in range(13):
            self.game_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        layout.addWidget(self.game_table)

        # Knappar
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Spara kupong")
        self.clear_button = QPushButton("Rensa")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_games(self):

        games = []

        for row in range(13):

            home_item = self.game_table.item(row, 0)
            away_item = self.game_table.item(row, 1)

            home = home_item.text() if home_item else ""
            away = away_item.text() if away_item else ""

            game = Game(row + 1, home, away)
            games.append(game)

        return games

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.year_week_widget.reset()
        for row in range(self.game_table.rowCount()):
            for col in range(self.game_table.columnCount()):
                item = self.game_table.item(row, col)
                if item:
                    item.setText("")
