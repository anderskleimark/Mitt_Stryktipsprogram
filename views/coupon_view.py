from mvc import View
from models.coupon_model import Game
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from misc.base_table_widget import BaseTableWidget


# Klass som har till uppgift att hantera vyn för att hantera tipskuponger.

class CouponView(View):

    # Skickas när användaren ändrar mål
    # row, home_score, away_score
    score_changed = Signal(int, int, int)

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.setLayout(self.layout)

        self.create_header("Kuponger")
        self.layout.addWidget(self.header)

        self.layout.addSpacing(25)

        # Year/Week widget (UI-komponent)
        self.year_week_widget = YearWeekWidget()
        self.layout.addWidget(self.year_week_widget)

        self.create_table()
        self.create_bottom_widget()

    def get_active_selection_table(self):
        return self.game_table

    # Funktion för att skapa tabellen med matcherna.
    def create_table(self):

        self.game_table = BaseTableWidget(False, False, 13, 5)
        self.game_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag", "Hemmamål", "Bortamål", "1X2"]
        )

        self.game_table.set_wide_columns([0, 1, 2, 3, 4])

        for row in range(13):
            self.game_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        # Gör målkolumnerna numeriska
        self.game_table.set_columns_numeric([2, 3])

        self.layout.addWidget(self.game_table)

    # Funktion som skapar widgeten med utskriftsknappen med mera.

    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.add_coupon_button = QPushButton("Lägg till")
        layout.addWidget(self.add_coupon_button)
        self.save_button = QPushButton("Spara")
        layout.addWidget(self.save_button)
        self.back_button = QPushButton("Tillbaka")
        layout.addWidget(self.back_button)
        self.print_button = QPushButton("Skriv ut")
        layout.addWidget(self.print_button)
        self.delete_button = QPushButton("Radera")
        self.delete_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion som uppdaterar vyn med den valda kupongen och dess matcher.
    def update_games(self, games):

        self.game_table.blockSignals(True)
        self.game_table.clearContents()
        self.game_table.setRowCount(len(games))

        for row, game in enumerate(games):

            self.game_table.setItem(row, 0, QTableWidgetItem(game.home_team))
            self.game_table.setItem(row, 1, QTableWidgetItem(game.away_team))

            self.game_table.setItem(
                row, 2,
                QTableWidgetItem(
                    "" if game.home_score is None else str(game.home_score))
            )

            self.game_table.setItem(
                row, 3,
                QTableWidgetItem(
                    "" if game.away_score is None else str(game.away_score))
            )

            # ⭐ 1X2
            self.game_table.setItem(
                row, 4,
                QTableWidgetItem(game.result_1x2)
            )
            # Gör IX2-kolumnen ej redigerbar.
            self.game_table.set_columns_readonly([4])

        self.game_table.blockSignals(False)

    # Funktion som hämtar de matcher som användaren fyllt i.
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

    # Funktion som aktiverar eller deaktiverar knapparna.
    def set_buttons_enabled(self, enabled):
        self.print_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def enter_view_mode(self):

        self.year_week_widget.set_active_status(True)
        self.game_table.show_columns([2, 3, 4])
        self.add_coupon_button.show()
        self.save_button.hide()
        self.add_coupon_button.show()
        self.print_button.show()
        self.delete_button.show()
        self.back_button.hide()
        self.header.setText("Kuponger")

    def enter_create_mode(self):

        self.year_week_widget.set_active_status(False)
        self.game_table.hide_columns([2, 3, 4])
        self.game_table.clearContents()
        self.game_table.setRowCount(13)
        self.save_button.show()
        self.add_coupon_button.hide()
        self.print_button.hide()
        self.delete_button.hide()
        self.back_button.show()
        self.header.setText("Ny kupong")

    # Funktion som rensar.

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.year_week_widget.reset()
        for row in range(self.game_table.rowCount()):
            for col in range(self.game_table.columnCount()):
                item = self.game_table.item(row, col)
                if item:
                    item.setText("")
