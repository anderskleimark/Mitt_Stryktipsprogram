from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidgetItem,
                               QWidget)

from misc.base_combo_box import BaseComboBox
from misc.base_table_widget import BaseTableWidget
from mvc import View
from widgets.year_week_widget import YearWeekWidget

# Klass som har till uppgift att hantera vyn för att hantera tipskuponger.


class CouponView(View):
    # Skickas när användaren ändrar mål
    # row, home_score, away_score
    score_changed = Signal(int, int, int)
    # Skickas när användaren ändrar Säsong
    season_changed = Signal(int, int)

    # Konstanter
    COMPETITION_COLUMN = 0
    HOME_TEAM_COLUMN = 1
    AWAY_TEAM_COLUMN = 2
    HOME_SCORE_COLUMN = 3
    AWAY_SCORE_COLUMN = 4
    RESULT_COLUMN = 5
    ROW_COUNT = 13
    COLUMN_COUNT = 6

    def __init__(self):
        super().__init__()

        self.coupon_table = None
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
        return self.coupon_table

    # Funktion för att skapa tabellen med matcherna.
    def create_table(self):
        self.coupon_table = BaseTableWidget(
            False, False, self.ROW_COUNT, self.COLUMN_COUNT)
        self.coupon_table.setHorizontalHeaderLabels(
            ["Tävling/liga", "Hemmalag", "Bortalag", "Hemmamål", "Bortamål", "1X2"]
        )

        self.coupon_table.set_wide_columns([0, 1, 2])

        for row in range(self.ROW_COUNT):
            self.coupon_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )
            # Tävling/liga
            league_combo = BaseComboBox()
            self.coupon_table.setCellWidget(
                row, self.COMPETITION_COLUMN, league_combo)

            # Hemmalag
            home_combo = BaseComboBox()
            self.coupon_table.setCellWidget(
                row, self.HOME_TEAM_COLUMN, home_combo)

            # Bortalag
            away_combo = BaseComboBox()
            self.coupon_table.setCellWidget(
                row, self.AWAY_TEAM_COLUMN, away_combo)

            # Koppla rätt rad
            league_combo.currentIndexChanged.connect(
                lambda index, row=row: self.emit_season_changed(row))

        # Gör målkolumnerna numeriska
        self.coupon_table.set_columns_numeric([3, 4])
        self.layout.addWidget(self.coupon_table)

    def set_seasons(self, seasons):
        for row in range(13):
            combo = self.coupon_table.cellWidget(row, self.COMPETITION_COLUMN)

            if combo is None:
                continue

            combo.blockSignals(True)
            combo.clear_with_empty_item()

            for season in seasons:
                combo.addItem(season.competition.name, season.id)

            combo.blockSignals(False)

            # Uppdatera lagen.
            if combo.count() > 0:
                self.emit_season_changed(row)

    # Funktion för att ställa in combo-boxarna för lagen.
    def set_teams(self, row, teams, home_team=None, away_team=None):
        home_combo = self.coupon_table.cellWidget(row, self.HOME_TEAM_COLUMN)
        away_combo = self.coupon_table.cellWidget(row, self.AWAY_TEAM_COLUMN)

        if home_combo is None or away_combo is None:
            return

        home_combo.blockSignals(True)
        away_combo.blockSignals(True)

        home_combo.clear()
        away_combo.clear()

        for team_id, team_name in teams:
            home_combo.addItem(team_name, team_id)
            away_combo.addItem(team_name, team_id)

        # Välj sparade lag
        if home_team:
            index = home_combo.findText(home_team)

            if index >= 0:
                home_combo.setCurrentIndex(index)

        if away_team:
            index = away_combo.findText(away_team)

            if index >= 0:
                away_combo.setCurrentIndex(index)

        home_combo.blockSignals(False)
        away_combo.blockSignals(False)

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
        self.coupon_table.blockSignals(True)
        self.coupon_table.setRowCount(13)

        # Ingen kupong finns
        if not coupon_matches:
            for row in range(13):
                for col in range(3):
                    combo = self.coupon_table.cellWidget(row, col)

                    if combo:
                        combo.blockSignals(True)
                        combo.clear()
                        combo.addItem("", None)
                        combo.blockSignals(False)

                for col in range(3, 6):
                    self.coupon_table.setItem(row, col, QTableWidgetItem(""))

            self.coupon_table.blockSignals(False)
            return

        # Visa befintlig kupong
        for row, coupon_match in enumerate(coupon_matches):
            match = coupon_match.soccer_match

            # Tävling/liga
            league_combo = self.coupon_table.cellWidget(
                row, self.COMPETITION_COLUMN)

            if league_combo:
                index = league_combo.findData(match.season.id)

                if index >= 0:
                    league_combo.setCurrentIndex(index)

            # Hemmamål
            self.coupon_table.setItem(
                row,
                self.HOME_SCORE_COLUMN,
                QTableWidgetItem(
                    "" if match.home_score is None else str(match.home_score)
                )
            )

            # Bortamål
            self.coupon_table.setItem(
                row,
                self.AWAY_SCORE_COLUMN,
                QTableWidgetItem(
                    "" if match.away_score is None else str(match.away_score)
                )
            )

            # 1X2
            self.coupon_table.setItem(
                row,
                self.RESULT_COLUMN,
                QTableWidgetItem(match.result_1x2)
            )

        self.coupon_table.set_columns_readonly([self.RESULT_COLUMN])
        self.coupon_table.blockSignals(False)

    # Funktion som hämtar angivna matcher.
    def get_coupon_matches(self):
        matches = []

        for row in range(13):
            league_combo = self.coupon_table.cellWidget(
                row, self.COMPETITION_COLUMN)
            home_combo = self.coupon_table.cellWidget(
                row, self.HOME_TEAM_COLUMN)
            away_combo = self.coupon_table.cellWidget(
                row, self.AWAY_TEAM_COLUMN)

            matches.append(
                {
                    "number": row + 1,
                    "season_id": (
                        league_combo.currentData()
                        if league_combo else None
                    ),
                    "home_team": (
                        home_combo.currentText().strip()
                        if home_combo else ""
                    ),
                    "away_team": (
                        away_combo.currentText().strip()
                        if away_combo else ""
                    )
                }
            )

        return matches

    # Funktion som aktiverar eller deaktiverar knapparna.
    def set_buttons_enabled(self, enabled):
        self.print_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    # Funktion som visar vyn med översikt över tipskuponger.
    def enter_view_mode(self):
        self.year_week_widget.set_active_status(True)
        self.coupon_table.show_columns(
            [
                self.COMPETITION_COLUMN,
                self.HOME_TEAM_COLUMN,
                self.AWAY_TEAM_COLUMN,
                self.HOME_SCORE_COLUMN,
                self.AWAY_TEAM_COLUMN,
                self.RESULT_COLUMN
            ]
        )
        self.add_coupon_button.show()
        self.save_button.hide()
        self.print_button.show()
        self.delete_button.show()
        self.back_button.hide()
        self.update_header_text("Kuponger")

    # Funktion som visar vyn, där man lägger till en ny tipskupong.
    def enter_create_mode(self):
        self.year_week_widget.set_active_status(False)
        self.coupon_table.setEnabled(True)
        self.coupon_table.hide_columns([3, 4, 5])

        # Ta inte bort comboboxarna
        self.coupon_table.setRowCount(13)

        self.save_button.show()
        self.add_coupon_button.hide()
        self.print_button.hide()
        self.delete_button.hide()
        self.back_button.show()
        self.update_header_text("Ny kupong")

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.year_week_widget.reset()

        for row in range(self.COLUMN_COUNT):
            # Behåll comboboxarna men välj tomt alternativ
            for col in range(3):
                combo = self.coupon_table.cellWidget(row, col)

                if combo:
                    combo.blockSignals(True)
                    combo.setCurrentIndex(0)
                    combo.blockSignals(False)

            # Rensa mål/resultat
            for col in range(3, 6):
                item = self.coupon_table.item(row, col)

                if item:
                    item.setText("")

    # Funktion som skickar signal till CouponController, om något val ändras.
    def emit_season_changed(self, row):
        league_combo = self.coupon_table.cellWidget(
            row, self.COMPETITION_COLUMN)

        if league_combo is None:
            return

        season_id = league_combo.currentData()

        home_combo = self.coupon_table.cellWidget(row, self.HOME_TEAM_COLUMN)
        away_combo = self.coupon_table.cellWidget(row, self.AWAY_TEAM_COLUMN)

        # Ingen säsong vald → rensa laglistorna
        if season_id is None:
            if home_combo:
                home_combo.clear()
                home_combo.addItem("", None)

            if away_combo:
                away_combo.clear()
                away_combo.addItem("", None)

            return

        # Annars hämtas lagen av controllern
        self.season_changed.emit(row, season_id)
