from PySide6.QtWidgets import (QLabel, QStackedWidget,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (AddButton, BackButton, DeleteButton, EditButton,
                          InfoButton, ShowTableButton)
from misc.dialogs.add_competition_dialog import AddCompetitionDialog
from misc.dialogs.add_match_dialog import AddMatchDialog
from misc.dialogs.add_season_dialog import AddSeasonDialog
from misc.dialogs.select_team_dialog import SelectTeamDialog
from mvc import View


class CompetitionView(View):
    """
        View för hantering av tävlingar, säsonger, lag och matcher.

        Visar översikt över tävlingar, detaljer för vald tävling samt
        serietabell med lagstatistik och matcher.
    """

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

    # Paneler
    LEFT_PANEL_STRETCH_FACTOR = 2
    RIGHT_PANEL_STRETCH_FACTOR = 2

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

        self.layout = self.create_main_layout()
        self.create_header("Tävlingar och ligor")
        self.layout.addWidget(self.header)

        # Matchknappar som används av controller
        self.matches_controlpanel_widget = QWidget()

        self.add_match_button = AddButton()
        self.edit_match_button = EditButton()
        self.delete_match_button = DeleteButton()

        # Innehållsväxling
        self.stacked_widget = QStackedWidget()

        # Skapa de widgetar som ska ingå i QStackedWidget
        self.create_overview_widget()
        self.create_details_widget()
        self.create_standings_widget()

        # Lägg till i QStackedWidget
        self.stacked_widget.addWidget(self.overview_widget)
        self.stacked_widget.addWidget(self.details_widget)
        self.stacked_widget.addWidget(self.standings_widget)

        self.layout.addWidget(self.stacked_widget)

        # Bottenknappar
        self.create_bottom_widget()
        self.setLayout(self.layout)
        self.show_overview()

    def create_overview_widget(self):
        """
            Skapar översikten med tävlingstabellen.
        """
        self.overview_widget = QWidget()

        layout = self.create_vertical_layout(parent=self.overview_widget)

        self.competition_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.OVERVIEW_COLUMN_COUNT
        )

        self.competition_table.setHorizontalHeaderLabels(self.OVERVIEW_HEADERS)

        self.competition_table.set_narrow_columns([
            self.OVERVIEW_ID_COLUMN,
            self.OVERVIEW_COUNTRY_COLUMN
        ])

        self.competition_table.set_wide_column(self.OVERVIEW_NAME_COLUMN)

        layout.addWidget(self.competition_table)
        layout.addSpacing(1)

    def create_details_widget(self):
        """
            Skapar detaljvyn för vald tävling.

            Vyn innehåller tabeller för säsonger och lag samt knappar
            för att lägga till och ta bort säsonger och lag.
        """
        self.details_widget = QWidget()
        layout = self.create_vertical_layout()

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
        season_buttons = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        self.add_season_button = AddButton()
        season_buttons.addWidget(self.add_season_button)

        self.delete_season_button = DeleteButton()
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
        team_buttons = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        self.add_team_button = AddButton()
        team_buttons.addWidget(self.add_team_button)

        self.delete_team_button = DeleteButton()
        team_buttons.addWidget(self.delete_team_button)
        team_buttons.addStretch()

        layout.addLayout(team_buttons)
        self.details_widget.setLayout(layout)

    def create_matches_controlpanel_widget(self):
        """
            Skapar kontrollpanel för att lägga till,
            redigera och ta bort matcher.
        """

        layout = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        layout.addWidget(self.add_match_button)
        layout.addWidget(self.edit_match_button)
        layout.addWidget(self.delete_match_button)

        layout.addStretch()

        self.matches_controlpanel_widget.setLayout(layout)

    def create_standings_widget(self):
        """
            Skapar vyn för serietabell och laginformation.

            Vyn innehåller serietabell, statistik för valt lag,
            lista över lagets matcher samt knappar för att hantera matcher.
        """
        self.standings_widget = QWidget()

        # Huvudlayout
        main_layout = self.create_horizontal_layout(
            parent=None,
            spacing=30
        )

        # Vänster panel
        left_widget = QWidget()
        left_layout = self.create_vertical_layout(
            parent=left_widget,
            spacing=None
        )

        left_layout.addWidget(QLabel(self.LABEL_STANDINGS))

        self.standings_table = BaseTableWidget(
            True,
            True,
            self.EMPTY_ROWS,
            self.STANDING_COLUMN_COUNT
        )

        self.standings_table.setHorizontalHeaderLabels(self.STANDING_HEADERS)
        self.standings_table.set_wide_column(self.STANDING_TEAM_COLUMN)

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
        right_layout = self.create_vertical_layout(
            parent=right_widget,
            spacing=None
        )

        # Rubrik
        self.team_info_label = QLabel()
        right_layout.addWidget(self.team_info_label)

        # Statistik
        statistics_label = QLabel(self.LABEL_STATISTICS)
        statistics_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(statistics_label)

        stats_widget = QWidget()
        stats_layout = self.create_grid_layout(
            parent=stats_widget,
        )

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

        self.team_matches_table.setHorizontalHeaderLabels(self.MATCH_HEADERS)

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
        main_layout.addWidget(
            left_widget, stretch=self.LEFT_PANEL_STRETCH_FACTOR)
        main_layout.addWidget(
            right_widget, stretch=self.RIGHT_PANEL_STRETCH_FACTOR)

        self.standings_widget.setLayout(main_layout)

    def create_bottom_widget(self):
        """
            Skapar den nedre knapppanelen.

            Innehåller knappar för navigering, visning av information,
            visning av serietabell samt hantering av tävlingar.
        """
        bottom_widget = QWidget()

        layout = self.create_horizontal_layout()

        # Knappar
        self.back_to_overview_button = BackButton()
        layout.addWidget(self.back_to_overview_button)

        self.back_to_details_button = BackButton()
        layout.addWidget(self.back_to_details_button)

        self.show_standing_table_button = ShowTableButton()
        layout.addWidget(self.show_standing_table_button)

        self.add_competition_button = AddButton()
        layout.addWidget(self.add_competition_button)

        self.show_info_button = InfoButton()
        layout.addWidget(self.show_info_button)

        self.delete_competition_button = DeleteButton()
        layout.addWidget(self.delete_competition_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    def update_competition_table(self, competitions):
        """
            Uppdaterar tabellen med tävlingar.
        """
        self.competition_table.clearContents()
        self.competition_table.setRowCount(len(competitions))

        for row, competition in enumerate(competitions):
            # Id
            self.competition_table.setItem(
                row,
                self.OVERVIEW_ID_COLUMN,
                QTableWidgetItem(str(competition.id))
            )

            # Land med flagga
            country_item = QTableWidgetItem(competition.country.display_name)
            country_item.setIcon(competition.country.flag_icon)

            self.competition_table.setItem(
                row,
                self.OVERVIEW_COUNTRY_COLUMN,
                country_item
            )

            # Namn
            self.competition_table.setItem(
                row,
                self.OVERVIEW_NAME_COLUMN,
                QTableWidgetItem(competition.competition_name)
            )

        # Anpassa kolumnbredder
        self.competition_table.set_narrow_columns(
            [
                self.OVERVIEW_ID_COLUMN
            ]
        )

        self.competition_table.set_wide_columns(
            [
                self.OVERVIEW_COUNTRY_COLUMN,
                self.OVERVIEW_NAME_COLUMN
            ]
        )

    def update_season_table(self, seasons):
        """
            Uppdaterar tabellen med säsonger.
        """
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

        self.season_table.set_wide_column(self.SEASON_NAME_COLUMN)

    def update_team_table(self, teams):
        """
            Uppdaterar tabellen med lag.
        """
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
                QTableWidgetItem(team.team_name)
            )

        # Anpassa kolumnbredder
        self.team_table.set_narrow_column(self.TEAM_ID_COLUMN)
        self.team_table.set_wide_column(self.TEAM_NAME_COLUMN)

    def update_competition_info(self, competition):
        """
            Uppdaterar information för vald tävling.
        """
        self.update_header_text(
            competition.competition_name,
            competition.country.flag_path
        )

    def update_standings_table(self, standings):
        """
            Uppdaterar serietabellen.
        """
        self.standings_table.clearContents()
        self.standings_table.setRowCount(len(standings))

        for row, standing in enumerate(standings):
            # Lag
            self.standings_table.setItem(
                row,
                self.STANDING_TEAM_COLUMN,
                QTableWidgetItem(standing.team.display_name)
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

    def update_team_statistics(self, standing):
        """
            Uppdaterar statistik för valt lag.
        """
        self.team_info_label.setText(standing.team.display_name)
        self.played_label.setText(str(standing.played))
        self.goals_label.setText(
            f"{standing.goals_for} – {standing.goals_against}")

        goal_difference = standing.goals_for - standing.goals_against

        self.goal_difference_label.setText(f"{goal_difference:+d}")
        self.points_label.setText(str(standing.points))

    def update_team_matches(self, matches):
        """
            Uppdaterar tabellen med lagets matcher.
        """
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
                QTableWidgetItem(match.home_team.display_name)
            )

            # Bortalag
            self.team_matches_table.setItem(
                row,
                self.MATCH_AWAY_COLUMN,
                QTableWidgetItem(match.away_team.display_name)
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

    def show_overview(self):
        """
            Visar översikten med tävlingar.
        """
        self.update_header_text("Tävlingar och ligor")
        self.back_to_overview_button.hide()
        self.add_competition_button.show()

        self.show_info_button.show()
        self.delete_competition_button.show()

        self.show_info_button.setEnabled(False)
        self.delete_competition_button.setEnabled(False)

        self.show_standing_table_button.hide()
        self.back_to_details_button.hide()

        self.clear()
        self.stacked_widget.setCurrentWidget(self.overview_widget)

    def show_details(self):
        """
            Visar detaljvyn för vald tävling.
        """
        self.back_to_overview_button.show()
        self.show_standing_table_button.show()
        self.add_competition_button.hide()
        self.show_info_button.hide()
        self.delete_competition_button.hide()
        self.back_to_details_button.hide()
        self.stacked_widget.setCurrentWidget(self.details_widget)

    def show_standings(self):
        """
            Visar serietabellsvyn.
        """
        self.back_to_overview_button.hide()
        self.show_standing_table_button.hide()
        self.back_to_details_button.show()
        self.add_match_button.setEnabled(False)
        self.edit_match_button.setEnabled(False)
        self.delete_match_button.setEnabled(False)
        self.stacked_widget.setCurrentWidget(self.standings_widget)

    def clear_selection(self):
        """
            Rensar aktuell tabellmarkering.
        """
        table = self.get_active_selection_table()

        if table:
            table.clearSelection()

            if table == self.standings_table:
                self.clear_team_information()

    def clear(self):
        """
            Rensar valda objekt och tabellmarkeringar.
        """
        self.competition_table.clearSelection()
        self.season_table.clearSelection()
        self.team_table.clearSelection()
        self.standings_table.clearSelection()
        self.team_matches_table.clearSelection()

    def clear_team_information(self):
        """
            Rensar information om valt lag.
        """
        self.team_info_label.setText(
            "Laginformation"
        )

        self.played_label.setText("-")
        self.goals_label.setText("-")
        self.goal_difference_label.setText("-")
        self.points_label.setText("-")

        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(0)

    def get_active_selection_table(self):
        """
            Returnerar den tabell som för närvarande används för val.
        """
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

    def show_add_competition_dialog(
        self,
        countries
    ):
        """
            Visar dialogen för att lägga till en tävling.
        """
        dialog = AddCompetitionDialog(
            countries=countries,
            parent=self
        )

        if not dialog.exec():
            return None

        return (
            dialog.competition_name,
            dialog.country_id
        )

    def show_add_season_dialog(self):
        """
            Visar dialogen för att lägga till en säsong.
        """
        dialog = AddSeasonDialog(
            parent=self
        )

        if not dialog.exec():
            return None

        return (
            dialog.start_year,
            dialog.end_year
        )

    def show_select_team_dialog(
        self,
        teams
    ):
        """
            Visar dialogen för att välja ett lag.
        """
        dialog = SelectTeamDialog(
            teams=teams,
            parent=self
        )

        if not dialog.exec():
            return None

        return dialog.team_id

    def show_match_dialog(
        self,
        current_team,
        teams,
        match=None
    ):
        """
            Visar dialogen för att lägga till
            eller redigera en match.
        """
        dialog = AddMatchDialog(
            current_team=current_team,
            teams=teams,
            match=match,
            parent=self
        )

        if not dialog.exec():
            return None

        return (
            dialog.home_team_id,
            dialog.away_team_id,
            dialog.match_date,
            dialog.home_score,
            dialog.away_score
        )
