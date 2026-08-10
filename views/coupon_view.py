from PySide6.QtCore import Signal
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QTableWidgetItem, QWidget

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (AddButton, BackButton, DeleteButton, PrintButton,
                          SaveButton)
from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View
from widgets.year_week_widget import YearWeekWidget


class CouponView(View):
    """
        Klass som hanterar vyn för stryktipskuponger.

        Ansvarar för att visa kuponger, skapa nya kuponger
        samt hantera användarens interaktion med tabellen.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    # Skickas när användaren ändrar mål.
    # row, home_score, away_score
    score_changed = Signal(int, int, int)

    # Skickas när användaren ändrar säsong.
    # row, season_id
    season_changed = Signal(int, int)

    # --------------------------------------------------
    # Tabell
    # --------------------------------------------------

    ROW_COUNT = 13
    COLUMN_COUNT = 6

    COMPETITION_COLUMN = 0
    HOME_TEAM_COLUMN = 1
    AWAY_TEAM_COLUMN = 2
    HOME_SCORE_COLUMN = 3
    AWAY_SCORE_COLUMN = 4
    RESULT_COLUMN = 5

    TABLE_HEADERS = (
        "Tävling/liga",
        "Hemmalag",
        "Bortalag",
        "Hemmamål",
        "Bortamål",
        "1X2"
    )

    WIDE_COLUMNS = (
        COMPETITION_COLUMN,
        HOME_TEAM_COLUMN,
        AWAY_TEAM_COLUMN
    )

    SCORE_COLUMNS = (
        HOME_SCORE_COLUMN,
        AWAY_SCORE_COLUMN
    )

    RESULT_COLUMNS = (
        HOME_SCORE_COLUMN,
        AWAY_SCORE_COLUMN,
        RESULT_COLUMN
    )

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Kuponger"
    CREATE_VIEW_TITLE = "Ny kupong"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    HEADER_BOTTOM_SPACING = 25

    def __init__(self):
        """
            Initierar vyn.

            Skapar rubrik, år/omgångsväljare,
            kupongtabell och knappar.
        """
        super().__init__()

        self.coupon_table = None
        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.layout.addSpacing(self.HEADER_BOTTOM_SPACING)

        self.year_week_widget = YearWeekWidget()
        self.layout.addWidget(self.year_week_widget)

        self.create_table()
        self.create_bottom_widget()

        self.setLayout(self.layout)

    def get_active_selection_table(self):
        """
            Returnerar den aktiva tabellen.
        """
        return self.coupon_table

    def create_table(self):
        """
            Skapar innehållswidgeten med kupongtabellen.

            Tabellen innehåller comboboxar för liga,
            hemma- och bortalag samt kolumner för resultat.
        """
        self.table_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.table_widget,
            spacing=None
        )

        self.coupon_table = BaseTableWidget(
            False,
            False,
            self.COLUMN_COUNT,
            self.ROW_COUNT
        )

        self.coupon_table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.coupon_table.set_wide_columns(self.WIDE_COLUMNS)

        for row in range(self.ROW_COUNT):
            self.coupon_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

            # Tävling/liga
            league_combo = BaseComboBox()

            self.coupon_table.setCellWidget(
                row,
                self.COMPETITION_COLUMN,
                league_combo
            )

            # Hemmalag
            home_combo = BaseComboBox()

            self.coupon_table.setCellWidget(
                row,
                self.HOME_TEAM_COLUMN,
                home_combo
            )

            # Bortalag
            away_combo = BaseComboBox()

            self.coupon_table.setCellWidget(
                row,
                self.AWAY_TEAM_COLUMN,
                away_combo
            )

            league_combo.currentIndexChanged.connect(
                lambda _index, row=row:
                self.emit_season_changed(row)
            )

        self.coupon_table.set_columns_numeric(self.SCORE_COLUMNS)

        layout.addWidget(self.coupon_table)
        self.layout.addWidget(self.table_widget)

    def create_bottom_widget(self):
        """
            Skapar panelen med knappar för kuponghantering.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.bottom_widget,
            spacing=None
        )

        self.add_coupon_button = AddButton()
        layout.addWidget(self.add_coupon_button)

        self.save_button = SaveButton()
        layout.addWidget(self.save_button)

        self.back_button = BackButton()
        layout.addWidget(self.back_button)

        self.print_button = PrintButton()
        layout.addWidget(self.print_button)

        self.delete_button = DeleteButton()
        layout.addWidget(self.delete_button)

        self.layout.addWidget(self.bottom_widget)

    def set_seasons(self, seasons):
        """
            Fyller samtliga ligacomboboxar
            med tillgängliga säsonger.
        """
        for row in range(self.ROW_COUNT):
            combo = self.coupon_table.cellWidget(
                row,
                self.COMPETITION_COLUMN
            )

            if combo is None:
                continue

            combo.blockSignals(True)
            combo.clear_with_empty_item()

            for season in seasons:
                combo.addItem(
                    season.competition.competition_name,
                    season.id
                )

            combo.blockSignals(False)

            if combo.count() > 1:
                combo.setCurrentIndex(0)

    def set_teams(
        self,
        row,
        teams,
        home_team_id=None,
        away_team_id=None
    ):
        """
            Uppdaterar hemma- och bortalagscomboboxarna
            för angiven rad.

            Om lag-id anges väljs dessa automatiskt.
        """
        home_combo = self.coupon_table.cellWidget(
            row,
            self.HOME_TEAM_COLUMN
        )

        away_combo = self.coupon_table.cellWidget(
            row,
            self.AWAY_TEAM_COLUMN
        )

        if home_combo is None or away_combo is None:
            return

        home_combo.blockSignals(True)
        away_combo.blockSignals(True)

        home_combo.clear_with_empty_item()
        away_combo.clear_with_empty_item()

        for team in teams:
            home_combo.addItem(
                team.display_name,
                team.id
            )

            away_combo.addItem(
                team.display_name,
                team.id
            )

        if home_team_id is not None:
            index = home_combo.findData(home_team_id)

            if index >= 0:
                home_combo.setCurrentIndex(index)

        if away_team_id is not None:
            index = away_combo.findData(away_team_id)

            if index >= 0:
                away_combo.setCurrentIndex(index)

        home_combo.blockSignals(False)
        away_combo.blockSignals(False)

        home_combo.setEnabled(True)
        away_combo.setEnabled(True)

    def update_coupon_matches(self, coupon_matches):
        """
            Uppdaterar tabellen med kupongens matcher.
            Om ingen kupong finns rensas tabellen.
        """
        self.coupon_table.blockSignals(True)
        self.coupon_table.setRowCount(self.ROW_COUNT)

        if not coupon_matches:
            self._clear_coupon_matches()
            self.coupon_table.blockSignals(False)

            return

        for row, coupon_match in enumerate(
            coupon_matches
        ):
            match = coupon_match.soccer_match

            league_combo = (
                self.coupon_table.cellWidget(
                    row,
                    self.COMPETITION_COLUMN
                )
            )

            if league_combo:
                league_combo.blockSignals(True)
                index = league_combo.findData(match.season.id)

                if index >= 0:
                    league_combo.setCurrentIndex(index)

                league_combo.blockSignals(False)

            self.coupon_table.setItem(
                row,
                self.HOME_SCORE_COLUMN,
                QTableWidgetItem(
                    ""
                    if match.home_score is None
                    else str(match.home_score)
                )
            )

            self.coupon_table.setItem(
                row,
                self.AWAY_SCORE_COLUMN,
                QTableWidgetItem(
                    ""
                    if match.away_score is None
                    else str(match.away_score)
                )
            )

            self.coupon_table.setItem(
                row,
                self.RESULT_COLUMN,
                QTableWidgetItem(match.result_1x2)
            )

        self.coupon_table.set_columns_readonly([self.RESULT_COLUMN])
        self.coupon_table.blockSignals(False)

    def _clear_coupon_matches(self):
        """
            Rensar samtliga matcher från kupongtabellen.
        """
        for row in range(self.ROW_COUNT):

            for column in range(
                self.COMPETITION_COLUMN,
                self.AWAY_TEAM_COLUMN + 1
            ):
                combo = self.coupon_table.cellWidget(
                    row,
                    column
                )

                if combo is None:
                    continue

                combo.blockSignals(True)
                combo.clear()
                combo.addItem("", None)
                combo.blockSignals(False)

            for column in self.RESULT_COLUMNS:
                self.coupon_table.setItem(
                    row,
                    column,
                    QTableWidgetItem("")
                )

    def get_coupon_matches(self):
        """
            Hämtar samtliga matcher från tabellen.
            Returnerar en lista med matchnummer,
            säsong och valda lag.
        """
        matches = []

        for row in range(self.ROW_COUNT):
            league_combo = (
                self.coupon_table.cellWidget(
                    row,
                    self.COMPETITION_COLUMN
                )
            )

            home_combo = (
                self.coupon_table.cellWidget(
                    row,
                    self.HOME_TEAM_COLUMN
                )
            )

            away_combo = (
                self.coupon_table.cellWidget(
                    row,
                    self.AWAY_TEAM_COLUMN
                )
            )

            matches.append(
                {
                    "number": row + 1,
                    "season_id": (
                        league_combo.currentData()
                        if league_combo
                        else None
                    ),
                    "home_team_id": (
                        home_combo.currentData()
                        if home_combo
                        else None
                    ),
                    "away_team_id": (
                        away_combo.currentData()
                        if away_combo
                        else None
                    )
                }
            )

        return matches

    def set_buttons_enabled(self, enabled):
        """
            Aktiverar eller inaktiverar
            utskrifts- och raderingsknapparna.
        """
        self.print_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def enter_view_mode(self):
        """
            Växlar till visningsläge.

            Visar resultatkolumner och knappar
            för utskrift och radering.
        """
        self.year_week_widget.set_active_status(True)

        self.coupon_table.show_columns([
            self.COMPETITION_COLUMN,
            self.HOME_TEAM_COLUMN,
            self.AWAY_TEAM_COLUMN,
            self.HOME_SCORE_COLUMN,
            self.AWAY_SCORE_COLUMN,
            self.RESULT_COLUMN
        ])

        self.add_coupon_button.show()
        self.save_button.hide()
        self.print_button.show()
        self.delete_button.show()
        self.back_button.hide()
        self.update_header_text(self.VIEW_TITLE)

    def enter_create_mode(self):
        """
            Växlar till läget för att skapa
            en ny kupong.
        """
        self.year_week_widget.set_active_status(False)
        self.coupon_table.setEnabled(True)
        self.coupon_table.hide_columns(self.RESULT_COLUMNS)
        self.coupon_table.setRowCount(self.ROW_COUNT)

        self.save_button.show()
        self.add_coupon_button.hide()
        self.print_button.hide()
        self.delete_button.hide()
        self.back_button.show()
        self.update_header_text(self.CREATE_VIEW_TITLE)

    def clear_form(self):
        """
            Återställer formuläret.
            Rensar år/omgång, comboboxar och
            resultatfält.
        """
        self.year_week_widget.reset()

        for row in range(self.ROW_COUNT):

            for column in range(
                self.COMPETITION_COLUMN,
                self.AWAY_TEAM_COLUMN + 1
            ):
                combo = self.coupon_table.cellWidget(
                    row,
                    column
                )

                if combo:
                    combo.blockSignals(True)
                    combo.setCurrentIndex(0)
                    combo.blockSignals(False)

            for column in self.RESULT_COLUMNS:
                item = self.coupon_table.item(
                    row,
                    column
                )

                if item:
                    item.setText("")

    def emit_season_changed(self, row):
        """
            Skickar signal när säsongen ändras.
            Om ingen säsong är vald rensas
            lagcomboboxarna.
        """
        league_combo = self.coupon_table.cellWidget(
            row,
            self.COMPETITION_COLUMN
        )

        if league_combo is None:
            return

        season_id = league_combo.currentData()

        home_combo = self.coupon_table.cellWidget(
            row,
            self.HOME_TEAM_COLUMN
        )

        away_combo = self.coupon_table.cellWidget(
            row,
            self.AWAY_TEAM_COLUMN
        )

        if season_id is None:
            if home_combo:
                home_combo.clear()
                home_combo.addItem("", None)

            if away_combo:
                away_combo.clear()
                away_combo.addItem("", None)

            return

        if home_combo:
            home_combo.setEnabled(False)

        if away_combo:
            away_combo.setEnabled(False)

        self.season_changed.emit(
            row,
            season_id
        )

    def print_document(self, document):
        """
            Visar utskriftsdialogen och skriver ut dokumentet.
        """
        printer = QPrinter()

        dialog = QPrintDialog(
            printer,
            self
        )

        if dialog.exec():
            document.print_(printer)
