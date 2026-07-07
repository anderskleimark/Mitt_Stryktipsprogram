from mvc import View
from models.coupon_model import SoccerMatch, CouponMatch
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton,
    QComboBox
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

        self.game_table = BaseTableWidget(False, False, 13, 6)
        self.game_table.setHorizontalHeaderLabels(
            ["Liga", "Hemmalag", "Bortalag", "Hemmamål", "Bortamål", "1X2"]
        )

        self.game_table.set_wide_columns([0, 1, 2])

        for row in range(13):
            self.game_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        # Gör målkolumnerna numeriska
        self.game_table.set_columns_numeric([3, 4])
        self.layout.addWidget(self.game_table)

    def set_seasons(self, seasons):
        for row in range(13):

            combo = self.game_table.cellWidget(row, 0)

            if combo is None:
                combo = QComboBox()
                self.game_table.setCellWidget(
                    row,
                    0,
                    combo
                )

            combo.blockSignals(True)
            combo.clear()

            for season_id, league_name, start_year, end_year in seasons:

                combo.addItem(
                    f"{league_name} {start_year}/{end_year}",
                    season_id
                )

            combo.blockSignals(False)

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
    def update_coupon_matches(self, coupon_matches):

        self.game_table.blockSignals(True)

        # Behåll 13 rader så comboboxarna finns kvar
        self.game_table.setRowCount(13)

        # Rensa gamla lag/resultat
        for row in range(13):

            for col in range(1, 6):
                self.game_table.setItem(
                    row,
                    col,
                    None
                )

        for row, coupon_match in enumerate(coupon_matches):

            match = coupon_match.soccer_match

            # Liga
            combo = self.game_table.cellWidget(row, 0)

            if combo:

                index = combo.findData(
                    match.season_id
                )

                if index >= 0:
                    combo.setCurrentIndex(index)

            # Hemmalag
            self.game_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    match.home_team
                )
            )

            # Bortalag
            self.game_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    match.away_team
                )
            )

            # Hemmamål
            self.game_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    "" if match.home_score is None
                    else str(match.home_score)
                )
            )

            # Bortamål
            self.game_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    "" if match.away_score is None
                    else str(match.away_score)
                )
            )

            # 1X2
            self.game_table.setItem(
                row,
                5,
                QTableWidgetItem(
                    match.result_1x2
                )
            )

        self.game_table.set_columns_readonly([5])
        self.game_table.blockSignals(False)

    # Funktion som hämtar angivna matcher.
    def get_coupon_matches(self):

        coupon_matches = []

        for row in range(13):

            league_widget = self.game_table.cellWidget(row, 0)

            season_id = None

            if league_widget:
                season_id = league_widget.currentData()

            home_item = self.game_table.item(row, 1)
            away_item = self.game_table.item(row, 2)

            home = home_item.text().strip() if home_item else ""
            away = away_item.text().strip() if away_item else ""

            match = SoccerMatch(
                None,
                season_id,
                home,
                away
            )

            coupon_matches.append(
                CouponMatch(
                    row + 1,
                    match
                )
            )

        return coupon_matches

    # Funktion som aktiverar eller deaktiverar knapparna.
    def set_buttons_enabled(self, enabled):
        self.print_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    # Funktion som visar vyn med översikt över tipskuponger.
    def enter_view_mode(self):

        self.year_week_widget.set_active_status(True)
        self.game_table.show_columns([0, 1, 2, 3, 4, 5])
        self.add_coupon_button.show()
        self.save_button.hide()
        self.print_button.show()
        self.delete_button.show()
        self.back_button.hide()
        self.header.setText("Kuponger")

    # Funktion som visar vyn, där man lägger till en ny tipskupong.
    def enter_create_mode(self):

        self.year_week_widget.set_active_status(False)
        self.game_table.setEnabled(True)
        self.game_table.hide_columns([3, 4, 5])

        # Ta inte bort comboboxarna
        self.game_table.setRowCount(13)

        self.save_button.show()
        self.add_coupon_button.hide()
        self.print_button.hide()
        self.delete_button.hide()
        self.back_button.show()
        self.header.setText("Ny kupong")

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.year_week_widget.reset()
        for row in range(self.game_table.rowCount()):
            for col in range(self.game_table.columnCount()):
                item = self.game_table.item(row, col)
                if item:
                    item.setText("")
