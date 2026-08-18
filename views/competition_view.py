from PySide6.QtWidgets import QStackedWidget, QWidget

from misc.buttons import (AddButton, BackButton, DeleteButton,
                          InfoButton, ShowTableButton)
from misc.dialogs.add_competition_dialog import AddCompetitionDialog
from misc.dialogs.add_match_dialog import AddMatchDialog
from misc.dialogs.add_season_dialog import AddSeasonDialog
from misc.dialogs.select_team_dialog import SelectTeamDialog
from mvc import View
from widgets.competition_details_widget import CompetitionDetailsWidget
from widgets.competition_overview_widget import CompetitionOverviewWidget
from widgets.competition_standings_widget import CompetitionStandingWidget


class CompetitionView(View):
    """
        Vy för hantering av tävlingar, säsonger,
        lag och matcher.

        Vyn innehåller en översikt över tävlingar,
        en detaljvy för säsonger och lag samt en
        serietabell med lagstatistik och matcher.
    """

    def __init__(self):
        """
            Initierar vyn och skapar dess
            underliggande widgetar och paneler.
        """
        super().__init__()

        self.layout = self.create_main_layout()
        self.create_header("Tävlingar och ligor")

        self.layout.addWidget(self.header)

        self.stacked_widget = QStackedWidget()

        self.overview_widget = CompetitionOverviewWidget()
        self.details_widget = CompetitionDetailsWidget()
        self.standings_widget = CompetitionStandingWidget()

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

    # --------------------------------------------------
    # Visningslägen
    # --------------------------------------------------

    def show_overview(self):
        """
            Visar översikten över tävlingar
            och anpassar bottenpanelen därefter.
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
            Visar serietabellsvyn och återställer matchknapparnas aktiva tillstånd.
        """
        self.back_to_overview_button.hide()
        self.show_standing_table_button.hide()
        self.back_to_details_button.show()

        self.set_add_match_button_status(False)
        self.set_edit_match_button_status(False)
        self.set_delete_match_button_status(False)

        self.stacked_widget.setCurrentWidget(self.standings_widget)

    # --------------------------------------------------
    # Markering
    # --------------------------------------------------

    def clear_selection(self):
        """
            Rensar markeringen i den aktiva tabellen.
        """
        table = self.get_active_selection_table()

        if table is None:
            return

        is_standings_table = (
            self.stacked_widget.currentWidget() == self.standings_widget
            and self.standings_widget.is_standings_table(table)
        )

        table.clearSelection()

        if is_standings_table:
            self.clear_team_information()

    def clear(self):
        """
            Rensar samtliga tabellmarkeringar i vyn.
        """
        self.overview_widget.clear_selection()

        self.details_widget.clear_team_selection()
        self.details_widget.clear_season_selection()

        self.standings_widget.clear_selection()

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
            return self.standings_widget.get_active_selection_table()

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
            Returnerar vald rad i tävlingsöversikten.
        """
        return self.overview_widget.get_selected_row()

    def update_competition_table(
        self,
        competitions
    ):
        """
            Uppdaterar tävlingsöversikten.
        """
        self.overview_widget.update_table(competitions)

    def update_season_table(
        self,
        seasons
    ):
        """
            Uppdaterar säsongstabellen i detaljvyn.
        """
        self.details_widget.update_season_table(seasons)

    def update_team_table(
        self,
        teams
    ):
        """
            Uppdaterar lagtabellen i detaljvyn.
        """
        self.details_widget.update_team_table(teams)

    def get_selected_season_row(self):
        """
            Returnerar vald rad i säsongstabellen.
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

    def update_standings_table(
        self,
        standings
    ):
        """
            Uppdaterar serietabellen.
        """
        self.standings_widget.update_standings_table(standings)

    def update_team_statistics(
        self,
        standing
    ):
        """
            Uppdaterar statistik för valt lag.
        """
        self.standings_widget.update_team_statistics(standing)

    def update_team_matches(
        self,
        matches
    ):
        """
            Uppdaterar matchtabellen för valt lag.
        """
        self.standings_widget.update_team_matches(matches)

    def get_selected_standing_row(self):
        """
            Returnerar vald rad i serietabellen.
        """
        return self.standings_widget.get_selected_team_row()

    def get_selected_match_row(self):
        """
            Returnerar vald rad i matchtabellen.
        """
        return self.standings_widget.get_selected_match_row()

    def select_standing_row(
        self,
        row
    ):
        """
            Markerar angiven rad i serietabellen.
        """
        self.standings_widget.select_team_row(row)

    def set_add_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen för att lägga till en match.
        """
        self.standings_widget.set_add_match_button_status(status)

    def set_edit_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen
            för att redigera en match.
        """
        self.standings_widget.set_edit_match_button_status(status)

    def set_delete_match_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar knappen för att ta bort en match.
        """
        self.standings_widget.set_delete_match_button_status(status)

    def clear_season_selection(self):
        """
            Rensar markeringen i säsongstabellen.
        """
        self.details_widget.clear_season_selection()

    def clear_team_information(self):
        """
            Rensar informationen om valt lag i serietabellsvyn.
        """
        self.standings_widget.clear_team_information()
