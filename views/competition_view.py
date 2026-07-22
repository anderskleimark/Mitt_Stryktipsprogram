from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QStackedWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.country import Country
from mvc import View

# Klass (View) som visar information om tävlingar/lag, tabeller med mera.


class CompetitionView(View):

    # Tabellstorlekar
    EMPTY_ROWS = 0
    OVERVIEW_COLUMN_COUNT = 3
    DETAIL_COLUMN_COUNT = 2
    TEAM_COLUMN_COUNT = 2
    STANDING_COLUMN_COUNT = 7
    MATCH_COLUMN_COUNT = 4

    # Kolumner - tävlingar
    OVERVIEW_ID_COLUMN = 0
    OVERVIEW_COUNTRY_COLUMN = 1
    OVERVIEW_NAME_COLUMN = 2

    # Kolumner - säsonger
    SEASON_ID_COLUMN = 0
    SEASON_NAME_COLUMN = 1

    # Kolumner - lag
    TEAM_ID_COLUMN = 0
    TEAM_NAME_COLUMN = 1

    # Kolumner - serietabell
    STANDING_TEAM_COLUMN = 0
    STANDING_PLAYED_COLUMN = 1
    STANDING_WON_COLUMN = 2
    STANDING_DRAW_COLUMN = 3
    STANDING_LOST_COLUMN = 4
    STANDING_GOALS_COLUMN = 5
    STANDING_POINTS_COLUMN = 6

    # Kolumner - matcher
    MATCH_DATE_COLUMN = 0
    MATCH_HOME_COLUMN = 1
    MATCH_AWAY_COLUMN = 2
    MATCH_RESULT_COLUMN = 3

    # Tabellrubriker
    OVERVIEW_HEADERS = [
        "Id",
        "Land",
        "Namn"
    ]

    SEASON_HEADERS = [
        "Id",
        "Säsong"
    ]

    TEAM_HEADERS = [
        "Id",
        "Lag"
    ]

    STANDING_HEADERS = [
        "Lag",
        "Sp",
        "V",
        "O",
        "F",
        "Mål",
        "Poäng"
    ]

    MATCH_HEADERS = [
        "Datum",
        "Hemmalag",
        "Bortalag",
        "Resultat"
    ]

    # Knapptexter
    BUTTON_BACK = "Tillbaka"
    BUTTON_ADD = "Lägg till"
    BUTTON_DELETE = "Radera"
    BUTTON_INFORMATION = "Visa information"
    BUTTON_TABLE = "Visa tabell"
    BUTTON_EDIT = "Redigera"
    MATCH_TEXT = "match"

    # Etiketter
    LABEL_STANDINGS = "Serie-tabell"
    LABEL_STATISTICS = "Statistik"
    LABEL_MATCHES = "Matcher"

    LABEL_PLAYED = "Matcher:"
    LABEL_GOALS = "Mål:"
    LABEL_GOAL_DIFFERENCE = "Målskillnad:"
    LABEL_POINTS = "Poäng:"

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Tävlingar och ligor")
        self.layout.addWidget(self.header)

        # Innehållsväxling
        self.stacked_widget = QStackedWidget()

        # Skapa de widgetar som ska ingå i QStackedWidget.
        self.create_overview_widget()
        self.create_details_widget()
        self.create_standings_widget()

        # Lägg till i QStackedWidget.
        self.stacked_widget.addWidget(self.overview_widget)
        self.stacked_widget.addWidget(self.details_widget)
        self.stacked_widget.addWidget(self.standings_widget)

        self.layout.addWidget(self.stacked_widget)

        # Knappar
        self.create_bottom_widget()

        self.setLayout(self.layout)
        self.show_overview()

    # Funktion som skapar tabellen med ligor.
    def create_overview_widget(self):
        self.overview_widget = QWidget()
        layout = QVBoxLayout()

        self.competition_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.OVERVIEW_COLUMN_COUNT
        )

        self.competition_table.setHorizontalHeaderLabels(
            self.OVERVIEW_HEADERS
        )

        self.competition_table.set_narrow_columns(
            [
                self.OVERVIEW_ID_COLUMN,
                self.OVERVIEW_COUNTRY_COLUMN
            ]
        )
        self.competition_table.set_wide_column(
            self.OVERVIEW_NAME_COLUMN
        )

        layout.addWidget(self.competition_table)
        self.overview_widget.setLayout(layout)

    # Funktion för att skapa detaljvyn.
    def create_details_widget(self):
        self.details_widget = QWidget()
        layout = QVBoxLayout()

        # Säsonger
        layout.addWidget(QLabel("Säsonger"))

        self.season_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.DETAIL_COLUMN_COUNT
        )
        self.season_table.setHorizontalHeaderLabels(self.SEASON_HEADERS)
        self.season_table.set_narrow_column(self.SEASON_ID_COLUMN)
        self.season_table.set_wide_column(self.SEASON_NAME_COLUMN)

        layout.addWidget(self.season_table)

        # Knappar för säsonger
        season_buttons = QHBoxLayout()

        self.add_season_button = QPushButton(f"{self.BUTTON_ADD} säsong")
        season_buttons.addWidget(self.add_season_button)

        self.delete_season_button = QPushButton(
            f"{self.BUTTON_DELETE} säsong"
        )
        season_buttons.addWidget(self.delete_season_button)
        season_buttons.addStretch()
        layout.addLayout(season_buttons)

        # Lag
        layout.addWidget(QLabel("Lag"))

        self.team_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.TEAM_COLUMN_COUNT
        )
        self.team_table.setHorizontalHeaderLabels(self.TEAM_HEADERS)
        self.team_table.set_narrow_column(self.TEAM_ID_COLUMN)
        self.team_table.set_wide_column(self.TEAM_NAME_COLUMN)

        layout.addWidget(self.team_table)

        # Knappar för lag
        team_buttons = QHBoxLayout()

        self.add_team_button = QPushButton(f"{self.BUTTON_ADD} lag")
        team_buttons.addWidget(self.add_team_button)

        self.delete_team_button = QPushButton(
            f"{self.BUTTON_DELETE} lag"
        )
        team_buttons.addWidget(self.delete_team_button)
        team_buttons.addStretch()

        layout.addLayout(team_buttons)
        self.details_widget.setLayout(layout)

    # Funktion för att skapa en kontrollpanel med knappar för att lägga till, redigera
    # och radera matcher för valt lag.
    def create_matches_controlpanel_widget(self):
        self.matches_controlpanel_widget = QWidget()

        layout = QHBoxLayout()

        self.add_match_button = QPushButton(
            f"{self.BUTTON_ADD} {self.MATCH_TEXT}"
        )
        layout.addWidget(self.add_match_button)

        self.edit_match_button = QPushButton(
            f"{self.BUTTON_EDIT} {self.MATCH_TEXT}"
        )
        layout.addWidget(self.edit_match_button)

        self.delete_match_button = QPushButton(
            f"{self.BUTTON_DELETE} {self.MATCH_TEXT}"
        )

        layout.addWidget(self.delete_match_button)
        layout.addStretch()
        self.matches_controlpanel_widget.setLayout(layout)

    # Funktion som skapar widget med ställningen.
    def create_standings_widget(self):
        self.standings_widget = QWidget()

        # Huvudlayout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(30)

        # Vänster panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel(self.LABEL_STANDINGS))

        self.standings_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.STANDING_COLUMN_COUNT
        )

        self.standings_table.setHorizontalHeaderLabels(
            self.STANDING_HEADERS
        )

        self.standings_table.set_wide_column(
            self.STANDING_TEAM_COLUMN
        )

        self.standings_table.set_narrow_columns(
            [
                self.STANDING_PLAYED_COLUMN,
                self.STANDING_WON_COLUMN,
                self.STANDING_DRAW_COLUMN,
                self.STANDING_LOST_COLUMN,
                self.STANDING_GOALS_COLUMN,
                self.STANDING_POINTS_COLUMN
            ]
        )

        left_layout.addWidget(self.standings_table, stretch=1)

        # Höger panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Rubrik
        self.team_info_label = QLabel()
        right_layout.addWidget(self.team_info_label)
        right_layout.addSpacing(8)

        # Statistik
        statistics_label = QLabel(self.LABEL_STATISTICS)
        statistics_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(statistics_label)

        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setHorizontalSpacing(10)
        stats_layout.setVerticalSpacing(4)

        stats_layout.addWidget(QLabel(self.LABEL_PLAYED), 0, 0)
        self.played_label = QLabel("-")
        stats_layout.addWidget(self.played_label, 0, 1)

        stats_layout.addWidget(QLabel(self.LABEL_GOALS), 1, 0)
        self.goals_label = QLabel("-")
        stats_layout.addWidget(self.goals_label, 1, 1)

        stats_layout.addWidget(QLabel(self.LABEL_GOAL_DIFFERENCE), 2, 0)
        self.goal_difference_label = QLabel("-")
        stats_layout.addWidget(self.goal_difference_label, 2, 1)

        stats_layout.addWidget(QLabel(self.LABEL_POINTS), 3, 0)
        self.points_label = QLabel("-")
        stats_layout.addWidget(self.points_label, 3, 1)

        right_layout.addWidget(stats_widget)
        right_layout.addSpacing(10)

        # Matcher
        matches_label = QLabel(self.LABEL_MATCHES)
        matches_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(matches_label)

        self.team_matches_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.MATCH_COLUMN_COUNT
        )

        self.team_matches_table.setHorizontalHeaderLabels(
            self.MATCH_HEADERS
        )

        self.team_matches_table.set_narrow_columns(
            [
                self.MATCH_DATE_COLUMN,
                self.MATCH_RESULT_COLUMN
            ]
        )

        self.team_matches_table.set_wide_columns(
            [
                self.MATCH_HOME_COLUMN,
                self.MATCH_AWAY_COLUMN
            ]
        )

        right_layout.addWidget(self.team_matches_table, stretch=1)

        self.create_matches_controlpanel_widget()
        right_layout.addWidget(self.matches_controlpanel_widget)

        # Lägg panelerna bredvid varandra
        main_layout.addWidget(left_widget, stretch=3)
        main_layout.addWidget(right_widget, stretch=2)

        self.standings_widget.setLayout(main_layout)

    # Funktion som skapar den undre widgeten med olika knappar.
    def create_bottom_widget(self):
        bottom_widget = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.back_to_overview_button = QPushButton(self.BUTTON_BACK)
        layout.addWidget(self.back_to_overview_button)

        self.back_to_details_button = QPushButton(self.BUTTON_BACK)
        layout.addWidget(self.back_to_details_button)

        self.show_standing_table_button = QPushButton(self.BUTTON_TABLE)
        layout.addWidget(self.show_standing_table_button)

        self.add_competition_button = QPushButton(self.BUTTON_ADD)
        layout.addWidget(self.add_competition_button)

        self.show_info_button = QPushButton(self.BUTTON_INFORMATION)
        layout.addWidget(self.show_info_button)

        self.delete_competition_button = QPushButton(self.BUTTON_DELETE)
        self.delete_competition_button.setProperty(
            "buttonClass",
            "warning"
        )
        layout.addWidget(self.delete_competition_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

        self.show_overview()

    # Funktion som körs, när tabellen med tävlingar/ligor uppdateras.
    def update_competition_table(self, competitions):
        self.competition_table.clearContents()
        self.competition_table.setRowCount(len(competitions))

        for row, competition in enumerate(competitions):
            # Id
            self.competition_table.setItem(
                row,
                self.OVERVIEW_ID_COLUMN,
                QTableWidgetItem(str(competition.id))
            )

            # Flagga
            country_item = QTableWidgetItem(competition.country)
            country_item.setIcon(
                QIcon(Country.get_flag_path(competition.country))
            )

            self.competition_table.setItem(
                row,
                self.OVERVIEW_COUNTRY_COLUMN,
                country_item
            )

            # Namn
            self.competition_table.setItem(
                row,
                self.OVERVIEW_NAME_COLUMN,
                QTableWidgetItem(competition.name)
            )

        # Anpassa kolumnbredder
        self.competition_table.set_narrow_columns(
            [
                self.OVERVIEW_ID_COLUMN,
                self.OVERVIEW_COUNTRY_COLUMN
            ]
        )

        self.competition_table.set_wide_column(
            self.OVERVIEW_NAME_COLUMN
        )

    # Funktion som körs, när tabellen med säsonger uppdateras.
    def update_season_table(self, seasons):
        self.season_table.clearContents()
        self.season_table.setRowCount(len(seasons))

        for row, season in enumerate(seasons):
            # Id
            self.season_table.setItem(
                row,
                self.SEASON_ID_COLUMN,
                QTableWidgetItem(str(season.id))
            )

            # Säsong
            self.season_table.setItem(
                row,
                self.SEASON_NAME_COLUMN,
                QTableWidgetItem(season.name)
            )

        # Anpassa kolumnbredder
        self.season_table.set_narrow_column(
            self.SEASON_ID_COLUMN
        )

        self.season_table.set_wide_column(
            self.SEASON_NAME_COLUMN
        )

    # Funktion som körs, när tabellen med lagen i säsongerna uppdateras.
    def update_team_table(self, teams):
        self.team_table.clearContents()
        self.team_table.setRowCount(len(teams))

        for row, team in enumerate(teams):
            # Id
            self.team_table.setItem(
                row,
                self.TEAM_ID_COLUMN,
                QTableWidgetItem(str(team.id))
            )

            # Lag
            self.team_table.setItem(
                row,
                self.TEAM_NAME_COLUMN,
                QTableWidgetItem(team.name)
            )

        # Anpassa kolumnbredder
        self.team_table.set_narrow_column(
            self.TEAM_ID_COLUMN
        )

        self.team_table.set_wide_column(
            self.TEAM_NAME_COLUMN
        )

    # Funktion för att uppdatera informationen om tävlingen/ligan.
    def update_competition_info(self, competition):
        self.update_header_text(
            competition.name,
            Country.get_flag_path(competition.country)
        )

    # Funktion för att uppdatera serie-tabellen.
    def update_standings_table(self, standings):
        self.standings_table.clearContents()
        self.standings_table.setRowCount(len(standings))

        for row, standing in enumerate(standings):
            # Lag
            self.standings_table.setItem(
                row,
                self.STANDING_TEAM_COLUMN,
                QTableWidgetItem(standing.name)
            )

            # Spelade
            self.standings_table.setItem(
                row,
                self.STANDING_PLAYED_COLUMN,
                QTableWidgetItem(str(standing.played))
            )

            # Vunna
            self.standings_table.setItem(
                row,
                self.STANDING_WON_COLUMN,
                QTableWidgetItem(str(standing.wins))
            )

            # Oavgjorda
            self.standings_table.setItem(
                row,
                self.STANDING_DRAW_COLUMN,
                QTableWidgetItem(str(standing.draws))
            )

            # Förlorade
            self.standings_table.setItem(
                row,
                self.STANDING_LOST_COLUMN,
                QTableWidgetItem(str(standing.losses))
            )

            # Mål
            self.standings_table.setItem(
                row,
                self.STANDING_GOALS_COLUMN,
                QTableWidgetItem(
                    f"{standing.goals_for} – {standing.goals_against}"
                )
            )

            # Poäng
            self.standings_table.setItem(
                row,
                self.STANDING_POINTS_COLUMN,
                QTableWidgetItem(str(standing.points))
            )

        # Anpassa kolumnbredder
        self.standings_table.set_wide_column(
            self.STANDING_TEAM_COLUMN
        )

        self.standings_table.set_narrow_columns(
            [
                self.STANDING_PLAYED_COLUMN,
                self.STANDING_WON_COLUMN,
                self.STANDING_DRAW_COLUMN,
                self.STANDING_LOST_COLUMN,
                self.STANDING_GOALS_COLUMN,
                self.STANDING_POINTS_COLUMN
            ]
        )

    # Funktion för att uppdatera statistiken för det valda laget.
    def update_team_statistics(self, standing):
        self.team_info_label.setText(standing.name)
        self.played_label.setText(str(standing.played))
        self.goals_label.setText(
            f"{standing.goals_for} – {standing.goals_against}")

        goal_difference = standing.goals_for - standing.goals_against

        self.goal_difference_label.setText(f"{goal_difference:+d}")
        self.points_label.setText(str(standing.points))

    # Funktion för att uppdatera information om lagets spelade matcher under säsongen.
    def update_team_matches(self, matches):
        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(len(matches))

        for row, match in enumerate(matches):
            # Datum
            self.team_matches_table.setItem(
                row,
                self.MATCH_DATE_COLUMN,
                QTableWidgetItem(str(match.match_date))
            )

            # Hemmalag
            self.team_matches_table.setItem(
                row,
                self.MATCH_HOME_COLUMN,
                QTableWidgetItem(match.home_team.name)
            )

            # Bortalag
            self.team_matches_table.setItem(
                row,
                self.MATCH_AWAY_COLUMN,
                QTableWidgetItem(match.away_team.name)
            )

            # Resultat
            result = ""

            if (
                match.home_score is not None
                and match.away_score is not None
            ):
                result = f"{match.home_score} – {match.away_score}"

            self.team_matches_table.setItem(
                row,
                self.MATCH_RESULT_COLUMN,
                QTableWidgetItem(result)
            )

        # Anpassa kolumnbredder
        self.team_matches_table.set_narrow_columns(
            [
                self.MATCH_DATE_COLUMN,
                self.MATCH_RESULT_COLUMN
            ]
        )

        self.team_matches_table.set_wide_columns(
            [
                self.MATCH_HOME_COLUMN,
                self.MATCH_AWAY_COLUMN
            ]
        )

    # Funktion för att visa översikten.
    def show_overview(self):
        self.update_header_text("Tävlingar och ligor")
        self.back_to_overview_button.hide()
        self.add_competition_button.show()
        self.show_info_button.show()
        self.delete_competition_button.show()
        self.show_standing_table_button.hide()
        self.back_to_details_button.hide()
        self.clear()
        self.stacked_widget.setCurrentWidget(self.overview_widget)

    # Funktion för att visa vyn med tabellerna med information om säsonger
    # och lag för en viss liga.
    def show_details(self):
        self.back_to_overview_button.show()
        self.show_standing_table_button.show()
        self.add_competition_button.hide()
        self.show_info_button.hide()
        self.delete_competition_button.hide()
        self.back_to_details_button.hide()
        self.stacked_widget.setCurrentWidget(self.details_widget)

    # Funktion för att visa serie-tabellen för vald säsong.
    def show_standings(self):
        self.back_to_overview_button.hide()
        self.show_standing_table_button.hide()
        self.back_to_details_button.show()
        self.add_match_button.setEnabled(False)
        self.edit_match_button.setEnabled(False)
        self.delete_match_button.setEnabled(False)
        self.stacked_widget.setCurrentWidget(self.standings_widget)

    def clear_selection(self):
        table = self.get_active_selection_table()

        if table:
            table.clearSelection()

            if table == self.standings_table:
                self.clear_team_information()

    # Funktion för att rensa och återställa.
    def clear(self):
        self.competition_table.clearSelection()
        self.season_table.clearSelection()
        self.team_table.clearSelection()

        if hasattr(self, "standings_table"):
            self.standings_table.clearSelection()

        if hasattr(self, "team_matches_table"):
            self.team_matches_table.clearSelection()

    # Funktion som rensar informationen om valt lag.
    def clear_team_information(self):
        self.team_info_label.setText(
            "Laginformation"
        )

        self.played_label.setText("-")
        self.goals_label.setText("-")
        self.goal_difference_label.setText("-")
        self.points_label.setText("-")

        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(0)

    # Superfunktion som ser till att alla markeringar försvinner,
    # om användaren klickar utanför tabellerna.
    def get_active_selection_table(self):
        if self.stacked_widget.currentWidget() == self.overview_widget:
            return self.competition_table

        if self.stacked_widget.currentWidget() == self.details_widget:
            # Om en säsong är markerad
            if self.season_table.selectedItems():
                return self.season_table

            # Om ett lag är markerat
            if self.team_table.selectedItems():
                return self.team_table

        if self.stacked_widget.currentWidget() == self.standings_widget:

            # Om ett lag i serietabellen är markerat
            if self.standings_table.selectedItems():
                return self.standings_table

            # Om en match i matchtabellen är markerad
            if self.team_matches_table.selectedItems():
                return self.team_matches_table

        return None
