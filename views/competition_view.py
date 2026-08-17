from PySide6.QtWidgets import QLabel, QStackedWidget, QTableWidgetItem, QWidget

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (AddButton, BackButton, DeleteButton, EditButton,
                          InfoButton, ShowTableButton)
from misc.dialogs.add_competition_dialog import AddCompetitionDialog
from misc.dialogs.add_match_dialog import AddMatchDialog
from misc.dialogs.add_season_dialog import AddSeasonDialog
from misc.dialogs.select_team_dialog import SelectTeamDialog
from mvc import View
from widgets.competition_details_widget import CompetitionDetailsWidget
from widgets.competition_overview_widget import CompetitionOverviewWidget


class CompetitionView(View):
    """
        Vy för hantering av tävlingar, säsonger,
        lag och matcher.

        Vyn innehåller en översikt över tävlingar,
        en detaljvy för säsonger och lag samt en
        serietabell med lagstatistik och matcher.
    """

    # --------------------------------------------------
    # Tabellstorlekar
    # --------------------------------------------------

    STANDING_COLUMN_COUNT = 7
    MATCH_COLUMN_COUNT = 4

    # --------------------------------------------------
    # Kolumner - serietabell
    # --------------------------------------------------

    STANDING_TEAM_COLUMN = 0
    STANDING_PLAYED_COLUMN = 1
    STANDING_WON_COLUMN = 2
    STANDING_DRAW_COLUMN = 3
    STANDING_LOST_COLUMN = 4
    STANDING_GOALS_COLUMN = 5
    STANDING_POINTS_COLUMN = 6

    # --------------------------------------------------
    # Kolumner - matcher
    # --------------------------------------------------

    MATCH_DATE_COLUMN = 0
    MATCH_HOME_COLUMN = 1
    MATCH_AWAY_COLUMN = 2
    MATCH_RESULT_COLUMN = 3

    # --------------------------------------------------
    # Paneler
    # --------------------------------------------------

    LEFT_PANEL_STRETCH_FACTOR = 2
    RIGHT_PANEL_STRETCH_FACTOR = 2

    # --------------------------------------------------
    # Tabellrubriker
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Etiketter
    # --------------------------------------------------

    LABEL_STANDINGS = "Serietabell"
    LABEL_STATISTICS = "Statistik"
    LABEL_MATCHES = "Matcher"

    LABEL_PLAYED = "Matcher:"
    LABEL_GOALS = "Mål:"
    LABEL_GOAL_DIFFERENCE = "Målskillnad:"
    LABEL_POINTS = "Poäng:"

    def __init__(self):
        """
            Initierar vyn och skapar dess
            underliggande widgetar och paneler.
        """
        super().__init__()

        self.layout = self.create_main_layout()
        self.create_header("Tävlingar och ligor")

        self.layout.addWidget(self.header)

        self.matches_controlpanel_widget = QWidget()

        self.add_match_button = AddButton()
        self.edit_match_button = EditButton()
        self.delete_match_button = DeleteButton()

        self.stacked_widget = QStackedWidget()

        self.overview_widget = CompetitionOverviewWidget()
        self.details_widget = CompetitionDetailsWidget()

        self.create_standings_widget()

        self.stacked_widget.addWidget(self.overview_widget)
        self.stacked_widget.addWidget(self.details_widget)
        self.stacked_widget.addWidget(self.standings_widget)

        self.layout.addWidget(
            self.stacked_widget,
            stretch=self.FULL_STRETCH
        )

        self.create_bottom_widget()
        self.add_bottom_panel(self.bottom_widget)
        self.setLayout(self.layout)

        self.show_overview()

    # --------------------------------------------------
    # Matchkontroller
    # --------------------------------------------------

    def create_matches_controlpanel_widget(self):
        """
            Skapar kontrollpanelen för att lägga till,
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

    # --------------------------------------------------
    # Serietabell
    # --------------------------------------------------

    def create_standings_widget(self):
        """
            Skapar sidan med serietabell,
            lagstatistik och matcher.

            Vänster sida visar serietabellen.
            Höger sida visar information om valt lag,
            statistik, lagets matcher och matchkontroller.
        """
        self.standings_widget = QWidget()

        main_layout = self.create_horizontal_layout(
            parent=None,
            spacing=30
        )

        left_widget = QWidget()

        left_layout = self.create_vertical_layout(
            parent=left_widget,
            spacing=None
        )

        left_layout.addWidget(QLabel(self.LABEL_STANDINGS))

        self.standings_table = BaseTableWidget(
            True,
            True,
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

        left_layout.addWidget(
            self.standings_table,
            stretch=1
        )

        right_widget = QWidget()

        right_layout = self.create_vertical_layout(
            parent=right_widget,
            spacing=None
        )

        self.team_info_label = QLabel()

        right_layout.addWidget(self.team_info_label)
        statistics_label = QLabel(self.LABEL_STATISTICS)

        statistics_label.setStyleSheet("font-weight: bold;")

        right_layout.addWidget(statistics_label)

        stats_widget = QWidget()

        stats_layout = self.create_grid_layout(parent=stats_widget)

        stats_layout.addWidget(
            QLabel(self.LABEL_PLAYED),
            0,
            0
        )

        self.played_label = QLabel("-")

        stats_layout.addWidget(
            self.played_label,
            0,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_GOALS),
            1,
            0
        )

        self.goals_label = QLabel("-")

        stats_layout.addWidget(
            self.goals_label,
            1,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_GOAL_DIFFERENCE),
            2,
            0
        )

        self.goal_difference_label = QLabel("-")

        stats_layout.addWidget(
            self.goal_difference_label,
            2,
            1
        )

        stats_layout.addWidget(
            QLabel(self.LABEL_POINTS),
            3,
            0
        )

        self.points_label = QLabel("-")

        stats_layout.addWidget(
            self.points_label,
            3,
            1
        )

        right_layout.addWidget(stats_widget)
        right_layout.addSpacing(10)

        matches_label = QLabel(self.LABEL_MATCHES)
        matches_label.setStyleSheet("font-weight: bold;")

        right_layout.addWidget(matches_label)

        self.team_matches_table = BaseTableWidget(
            True,
            True,
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

        right_layout.addWidget(
            self.team_matches_table,
            stretch=1
        )

        self.create_matches_controlpanel_widget()

        right_layout.addWidget(self.matches_controlpanel_widget)

        main_layout.addWidget(
            left_widget,
            stretch=self.LEFT_PANEL_STRETCH_FACTOR
        )

        main_layout.addWidget(
            right_widget,
            stretch=self.RIGHT_PANEL_STRETCH_FACTOR
        )

        self.standings_widget.setLayout(main_layout)

    # --------------------------------------------------
    # Bottenpanel
    # --------------------------------------------------

    def create_bottom_widget(self):
        """
            Skapar den nedre knapppanelen.

            Panelen innehåller knappar för navigering,
            tävlingshantering och visning av serietabell.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.bottom_widget,
            spacing=None
        )

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

    # --------------------------------------------------
    # Uppdatering
    # --------------------------------------------------

    def update_competition_info(
        self,
        competition
    ):
        """
            Uppdaterar huvudrubriken med information
            om vald tävling och dess land.
        """
        self.update_header_text(
            competition.competition_name,
            competition.country.flag_path
        )

    def update_standings_table(
        self,
        standings
    ):
        """
            Uppdaterar serietabellen med
            aktuell lagstatistik.
        """
        self.standings_table.clearContents()

        self.standings_table.setRowCount(len(standings))

        for row, standing in enumerate(
            standings
        ):
            self.standings_table.setItem(
                row,
                self.STANDING_TEAM_COLUMN,
                QTableWidgetItem(standing.team.display_name)
            )

            self.standings_table.setItem(
                row,
                self.STANDING_PLAYED_COLUMN,
                QTableWidgetItem(str(standing.played))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_WON_COLUMN,
                QTableWidgetItem(str(standing.wins))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_DRAW_COLUMN,
                QTableWidgetItem(str(standing.draws))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_LOST_COLUMN,
                QTableWidgetItem(str(standing.losses))
            )

            self.standings_table.setItem(
                row,
                self.STANDING_GOALS_COLUMN,
                QTableWidgetItem(
                    f"{standing.goals_for} – "
                    f"{standing.goals_against}"
                )
            )

            self.standings_table.setItem(
                row,
                self.STANDING_POINTS_COLUMN,
                QTableWidgetItem(str(standing.points))
            )

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

    def update_team_statistics(
        self,
        standing
    ):
        """
            Uppdaterar statistikfältet för
            det valda laget.
        """
        self.team_info_label.setText(standing.team.display_name)

        self.played_label.setText(str(standing.played))

        self.goals_label.setText(
            f"{standing.goals_for} – "
            f"{standing.goals_against}"
        )

        goal_difference = (
            standing.goals_for
            - standing.goals_against
        )

        self.goal_difference_label.setText(f"{goal_difference:+d}")
        self.points_label.setText(str(standing.points))

    def update_team_matches(
        self,
        matches
    ):
        """
            Uppdaterar matchtabellen med
            matcher för valt lag.
        """
        self.team_matches_table.clearContents()

        self.team_matches_table.setRowCount(len(matches))

        for row, match in enumerate(
            matches
        ):
            self.team_matches_table.setItem(
                row,
                self.MATCH_DATE_COLUMN,
                QTableWidgetItem(str(match.match_date))
            )

            self.team_matches_table.setItem(
                row,
                self.MATCH_HOME_COLUMN,
                QTableWidgetItem(match.home_team.display_name)
            )

            self.team_matches_table.setItem(
                row,
                self.MATCH_AWAY_COLUMN,
                QTableWidgetItem(match.away_team.display_name)
            )

            result = ""

            if match.home_score is not None and match.away_score is not None:
                result = f"{match.home_score} – {match.away_score}"

            self.team_matches_table.setItem(
                row,
                self.MATCH_RESULT_COLUMN,
                QTableWidgetItem(result)
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

    # --------------------------------------------------
    # Visningslägen
    # --------------------------------------------------

    def show_overview(self):
        """
            Visar översikten över tävlingar
            och anpassar bottenpanelen därefter.
        """
        self.update_header_text(
            "Tävlingar och ligor"
        )

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
            Visar detaljvyn för vald tävling och anpassar bottenpanelen därefter.
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
            Visar serietabellsvyn och återställer
            matchknapparnas aktiva tillstånd.
        """
        self.back_to_overview_button.hide()
        self.show_standing_table_button.hide()
        self.back_to_details_button.show()

        self.add_match_button.setEnabled(False)
        self.edit_match_button.setEnabled(False)

        self.delete_match_button.setEnabled(False)
        self.stacked_widget.setCurrentWidget(self.standings_widget)

    # --------------------------------------------------
    # Markering
    # --------------------------------------------------

    def clear_selection(self):
        """
            Rensar markeringen i den aktiva
            tabellen.
        """
        table = self.get_active_selection_table()

        if table:
            table.clearSelection()

            if table == self.standings_table:
                self.clear_team_information()

    def clear(self):
        """
            Rensar samtliga tabellmarkeringar
            i vyn.
        """
        self.overview_widget.clear_selection()
        self.details_widget.clear_team_selection()
        self.details_widget.clear_season_selection()

        self.standings_table.clearSelection()
        self.team_matches_table.clearSelection()

    def clear_team_information(self):
        """
            Rensar informationen och matchlistan för det valda laget.
        """
        self.team_info_label.setText("Laginformation")

        self.played_label.setText("-")
        self.goals_label.setText("-")
        self.goal_difference_label.setText("-")
        self.points_label.setText("-")

        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(0)

    def get_active_selection_table(self):
        """
            Returnerar den tabell som för närvarande
            används för radmarkering.

            Returnerar None om ingen tabell har
            en aktiv markering.
        """
        current_widget = self.stacked_widget.currentWidget()

        if current_widget == self.overview_widget:
            return self.overview_widget.get_active_selection_table()

        if current_widget == self.details_widget:
            return self.details_widget.get_active_selection_table()

        if current_widget == self.standings_widget:
            if self.standings_table.selectedItems():
                return self.standings_table

            if self.team_matches_table.selectedItems():
                return self.team_matches_table

        return None

    # --------------------------------------------------
    # Dialoger
    # --------------------------------------------------

    def show_add_competition_dialog(
        self,
        countries
    ):
        """
            Visar dialogen för att lägga till
            en ny tävling.

            Returnerar tävlingsnamn och land-id,
            eller None om dialogen avbryts.
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
            Visar dialogen för att lägga till
            en ny säsong.

            Returnerar start- och slutår,
            eller None om dialogen avbryts.
        """
        dialog = AddSeasonDialog(parent=self)

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

            Returnerar valt lag-id eller None
            om dialogen avbryts.
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

            Returnerar lag-id:n, datum och resultat,
            eller None om dialogen avbryts.
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

    # --------------------------------------------------
    # Delegationsmetoder
    # --------------------------------------------------

    def get_selected_competition_row(self):
        """
            Returnerar vald rad i
            tävlingsöversikten.
        """
        return self.overview_widget.get_selected_row()

    def update_competition_table(
        self,
        competitions
    ):
        """
            Uppdaterar tävlingsöversikten.
        """
        self.overview_widget.update_table(
            competitions
        )

    def update_season_table(
        self,
        seasons
    ):
        """
            Uppdaterar säsongstabellen
            i detaljvyn.
        """
        self.details_widget.update_season_table(
            seasons
        )

    def update_team_table(
        self,
        teams
    ):
        """
            Uppdaterar lagtabellen
            i detaljvyn.
        """
        self.details_widget.update_team_table(
            teams
        )

    def get_selected_season_row(self):
        """
            Returnerar vald rad i
            säsongstabellen.
        """
        return self.details_widget.get_selected_season_row()

    def get_selected_team_row(self):
        """
            Returnerar vald rad i lagtabellen.
        """
        return self.details_widget.get_selected_team_row()

    def set_add_team_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen för att lägga till ett lag.
        """
        self.details_widget.add_team_button.setEnabled(status)

    def set_delete_team_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att ta bort ett lag.
        """
        self.details_widget.delete_team_button.setEnabled(status)

    def set_add_season_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att lägga till en säsong.
        """
        self.details_widget.add_season_button.setEnabled(status)

    def set_delete_season_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen för att ta bort en säsong.
        """
        self.details_widget.delete_season_button.setEnabled(status)

    def clear_season_selection(self):
        """
            Rensar markeringen i
            säsongstabellen.
        """
        self.details_widget.clear_season_selection()
