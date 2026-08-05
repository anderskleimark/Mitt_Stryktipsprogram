from PySide6.QtCore import QDate

from misc.dialogs.add_competition_dialog import AddCompetitionDialog
from misc.dialogs.add_match_dialog import AddMatchDialog
from misc.dialogs.add_season_dialog import AddSeasonDialog
from misc.dialogs.select_team_dialog import SelectTeamDialog
from mvc import Controller


class CompetitionController(Controller):
    """
        Controller som hanterar tävlingar, säsonger, lag och matcher.
    """

    def __init__(self, competition_model, soccer_model, country_model, view):
        """
            Initierar klassen.
        """
        super().__init__(view)
        self.competition_model = competition_model
        self.soccer_model = soccer_model
        self.country_model = country_model

        # Länder, ligor, säsonger, matcher och lag
        self.countries = []
        self.competitions = []
        self.seasons = []
        self.teams = []

        # Alla matcher i den valda säsongen
        self.season_matches = []

        # Matcher för det valda laget
        self.selected_team_matches = []

        self.selected_competition = None
        self.selected_season = None
        self.selected_team = None
        self.selected_match = None

    def on_show_view(self):
        """
            Uppdaterar tävlingsvyn innan den visas.
        """
        self.add_connections()
        self.load_countries()
        self.load_competitions()

        # Initialt läge
        self.view.delete_season_button.setEnabled(False)
        self.view.add_team_button.setEnabled(False)
        self.view.delete_team_button.setEnabled(False)
        self.view.show_info_button.setEnabled(False)
        self.view.delete_competition_button.setEnabled(False)
        self.view.show_standing_table_button.setEnabled(False)
        self.view.update_competition_table(self.competitions)

    def add_connections(self):
        """
            Kopplar samman signaler och slots.
        """
        self.view.competition_table.itemSelectionChanged.connect(
            self.on_competition_selection_changed)
        self.view.add_competition_button.clicked.connect(
            self.on_add_competition_button_clicked)
        self.view.delete_competition_button.clicked.connect(
            self.on_delete_competition_button_clicked)
        self.view.show_info_button.clicked.connect(
            self.on_show_info_button_clicked)
        self.view.back_to_overview_button.clicked.connect(
            self.on_back_to_overview_button_clicked)
        self.view.season_table.itemSelectionChanged.connect(
            self.on_season_selection_changed)
        self.view.add_season_button.clicked.connect(
            self.on_add_season_button_clicked)
        self.view.delete_season_button.clicked.connect(
            self.on_delete_season_button_clicked)
        self.view.add_team_button.clicked.connect(
            self.on_add_team_button_clicked)
        self.view.delete_team_button.clicked.connect(
            self.on_delete_team_button_clicked)
        self.view.team_table.itemSelectionChanged.connect(
            self.on_season_table_team_selection_changed)
        self.view.show_standing_table_button.clicked.connect(
            self.on_show_standing_table_button_clicked)
        self.view.back_to_details_button.clicked.connect(
            self.on_back_to_details_button_clicked)
        self.view.standings_table.itemSelectionChanged.connect(
            self.on_standings_table_team_selection_changed)
        self.view.team_matches_table.itemSelectionChanged.connect(
            self.on_team_matches_table_selection_changed)
        self.view.add_match_button.clicked.connect(
            self.on_add_match_button_clicked)
        self.view.edit_match_button.clicked.connect(
            self.on_edit_match_button_clicked)
        self.view.delete_match_button.clicked.connect(
            self.on_delete_match_button_clicked)

    def load_countries(self):
        """
            Hämtar alla länder.
        """
        self.countries = self.country_model.get_all_countries()

    def load_competitions(self):
        """
            Hämtar alla tävlingar.
        """
        self.competitions = self.competition_model.get_all()

    def load_teams(self):
        """
            Hämtar alla lag i den valda säsongen.
        """
        if not self.has_selected_season():
            self.teams = []
            return

        self.teams = self.soccer_model.get_teams_in_season(
            self.selected_season.id)

    def load_season_matches(self):
        """
            Hämtar alla matcher för den valda säsongen.
        """
        if not self.has_selected_season():
            self.season_matches = []
            return

        self.season_matches = self.soccer_model.get_matches(
            self.selected_season.id
        )

    def load_selected_team_matches(self):
        """
            Hämtar matcher för det valda laget.
        """
        if not self.has_selected_season() or not self.has_selected_team():
            self.selected_team_matches = []
            return

        self.selected_team_matches = self.soccer_model.get_matches(
            self.selected_season.id,
            self.selected_team.id
        )

    def on_competition_selection_changed(self):
        """
            Hanterar ändrad markering av tävling.
        """
        row = self.view.competition_table.get_selected_row()

        if 0 <= row < len(self.competitions):
            self.selected_competition = self.competitions[row]
        else:
            self.selected_competition = None

        enabled = self.selected_competition is not None

        self.view.delete_competition_button.setEnabled(enabled)
        self.view.show_info_button.setEnabled(enabled)

    def on_add_competition_button_clicked(self):
        """
            Lägger till en ny tävling.
        """
        dialog = AddCompetitionDialog(
            countries=self.countries,
            parent=self.view
        )

        if dialog.exec():
            try:
                self.competition_model.add_competition(
                    dialog.competition_name, dialog.country_id)
                self.load_competitions()
                self.view.update_competition_table(self.competitions)

            except ValueError as e:
                self.view.show_warning_message("Fel", str(e))

    def on_show_info_button_clicked(self):
        """
            Visar information om den valda tävlingen.
        """
        if not self.has_selected_competition():
            return

        self.view.update_competition_info(self.selected_competition)
        self.seasons = self.soccer_model.get_seasons(
            self.selected_competition.id
        )
        self.view.update_season_table(self.seasons)

        self.selected_season = None
        self.view.season_table.clearSelection()
        self.view.update_team_table([])

        self.view.show_details()

    def on_delete_competition_button_clicked(self):
        """
            Tar bort den valda tävlingen.
        """
        if not self.has_selected_competition():
            return

        # Dialogruta.
        confirmed = self.view.ask_question(
            "Radera tävlingen/ligan",
            "Är du säker på att du vill radera tävlingen/ligan och alla dess data?"
        )

        if not confirmed:
            return

        # Radering sker.
        self.competition_model.delete(self.selected_competition.id)
        self.load_competitions()
        self.view.delete_competition_button.setEnabled(False)
        self.view.update_competition_table(self.competitions)
        self.selected_competition = None

    def on_back_to_overview_button_clicked(self):
        """
            Visar översiktsvyn.
        """
        self.view.show_overview()

    def on_season_selection_changed(self):
        """
            Hanterar ändrad markering av säsong.
        """
        # Vald rad.
        row = self.view.season_table.get_selected_row()

        if row < 0 or row >= len(self.seasons):

            self.clear_selected_team()
            self.view.add_team_button.setEnabled(False)
            self.view.show_standing_table_button.setEnabled(False)
            return

        self.view.delete_season_button.setEnabled(True)
        self.view.add_team_button.setEnabled(True)
        self.view.delete_team_button.setEnabled(False)
        self.selected_season = self.seasons[row]
        self.view.show_standing_table_button.setEnabled(True)
        self.view.update_header_text(
            self.selected_season.display_name,
            self.selected_season.competition.country.flag_path

        )
        self.load_teams()
        self.load_season_matches()
        self.view.update_team_table(self.teams)
        self.clear_selected_team()

    def on_add_season_button_clicked(self):
        """
            Lägger till en ny säsong.
        """
        # Ingen tävling/liga vald.
        if not self.has_selected_competition():
            return

        # Dialog för att lägga till en ny säsong.
        dialog = AddSeasonDialog(parent=self.view)

        if dialog.exec():
            try:
                # Tillägg av säsong.
                self.competition_model.add_season(
                    self.selected_competition.id,
                    dialog.start_year,
                    dialog.end_year
                )

                # Säsonger.
                self.seasons = self.soccer_model.get_seasons(
                    self.selected_competition.id
                )

                # Uppdatering av tabellen med säsongerna.
                self.view.update_season_table(
                    self.seasons
                )

            except ValueError as e:
                self.view.show_warning(
                    "Fel",
                    str(e)
                )

    def on_delete_season_button_clicked(self):
        """
            Tar bort den valda säsongen.
        """
        # Ingen säsong är vald.
        if not self.has_selected_season():
            return

        confirmed = self.view.ask_question(
            "Radera säsong", "Vill du radera säsongen?")
        if not confirmed:
            return

        # Radering sker.
        self.competition_model.delete_season(self.selected_season.id)
        self.selected_season = None
        self.view.delete_season_button.setEnabled(False)
        self.view.delete_team_button.setEnabled(False)
        self.seasons = self.soccer_model.get_seasons(
            self.selected_competition.id)

        # Uppdatera vyn.
        self.view.update_season_table(self.seasons)
        self.view.update_team_table([])

    def on_add_team_button_clicked(self):
        """
            Lägger till ett befintligt lag i säsongen.
        """

        if not self.has_selected_season():
            return

        available_teams = self.soccer_model.get_available_teams(
            self.selected_season.id,
            self.selected_season.competition.country.id
        )

        dialog = SelectTeamDialog(
            available_teams,
            self.view
        )

        if dialog.exec():
            try:
                self.soccer_model.add_team_to_season(
                    self.selected_season.id,
                    dialog.team_id
                )

                self.load_teams()
                self.view.update_team_table(
                    self.teams
                )

            except ValueError as e:
                self.view.show_warning(
                    "Fel",
                    str(e)
                )

    def on_delete_team_button_clicked(self):
        """
            Tar bort det valda laget från säsongen.
        """
        if not self.has_selected_season():
            return

        if not self.has_selected_team():
            return

        team_name = self.selected_team.name

        confirmed = self.view.ask_question(
            "Ta bort lag",
            f"Vill du ta bort {team_name} från säsongen?"
        )
        if not confirmed:
            return

        try:
            self.soccer_model.remove_team_from_season(
                self.selected_season.id,
                self.selected_team.id
            )

        except ValueError as error:
            self.view.show_warning(
                "Kan inte ta bort laget",
                str(error)
            )
            return

        self.view.show_information(
            "Laget borttaget",
            f"{team_name} har tagits bort från säsongen."
        )

        self.load_teams()
        self.view.update_team_table(self.teams)
        self.view.delete_team_button.setEnabled(False)
        self.clear_selected_team()

    def on_season_table_team_selection_changed(self):
        """
            Hanterar ändrad markering av lag i säsongsvyn.
        """
        row = self.view.team_table.get_selected_row()

        if row < 0 or row >= len(self.teams):
            self.selected_team = None
            self.view.delete_team_button.setEnabled(False)
            return

        self.view.delete_team_button.setEnabled(True)
        self.selected_team = self.teams[row]

    def on_show_standing_table_button_clicked(self):
        """
            Visar serietabellen.
        """
        if not self.has_selected_season():
            return

        # Uppdatera serietabellen
        standings = self.get_standings()
        self.view.update_standings_table(standings)
        self.view.show_standings()

    def on_back_to_details_button_clicked(self):
        """
            Visar detaljvyn.
        """
        self.view.clear()
        self.view.show_details()

    def on_add_match_button_clicked(self):
        """
            Lägger till en ny match.
        """
        if not self.has_selected_team():
            return

        opponents = [
            team for team in self.teams
            if team.id != self.selected_team.id
        ]

        dialog = AddMatchDialog(self.selected_team, opponents, self.view)

        if dialog.exec():
            if dialog.home:
                home_team_id = self.selected_team.id
                away_team_id = dialog.opponent_id
            else:
                home_team_id = dialog.opponent_id
                away_team_id = self.selected_team.id

            if self.soccer_model.match_exists(
                self.selected_season.id,
                home_team_id,
                away_team_id
            ):
                self.view.show_warning(
                    "Match finns redan",
                    "Den matchen finns redan tillagd."
                )
                return

            self.soccer_model.add_match(
                self.selected_season.id,
                home_team_id,
                away_team_id,
                dialog.match_date,
                dialog.home_score,
                dialog.away_score
            )

            self.refresh_selected_team()

    def on_edit_match_button_clicked(self):
        """
            Redigerar den valda matchen.
        """
        if (
            not self.has_selected_season() or not self.has_selected_team()
                or not self.has_selected_match()
        ):
            return

        match = self.selected_match

        opponents = [
            team for team in self.teams
            if team.id != self.selected_team.id
        ]

        dialog = AddMatchDialog(
            self.selected_team,
            opponents,
            self.view
        )

        # Hemma/borta
        if match.home_team.id == self.selected_team.id:
            dialog.home_away_combo.setCurrentIndex(0)
            opponent_id = match.away_team.id
        else:
            dialog.home_away_combo.setCurrentIndex(1)
            opponent_id = match.home_team.id

        # Motståndare
        index = dialog.opponent_combo.findData(opponent_id)

        if index >= 0:
            dialog.opponent_combo.setCurrentIndex(index)

        # Datum
        date = QDate.fromString(
            match.match_date,
            "yyyy-MM-dd"
        )
        dialog.date_edit.setDate(date)

        # Resultat
        if match.home_score is not None:
            dialog.home_score_spin.setValue(match.home_score)

        if match.away_score is not None:
            dialog.away_score_spin.setValue(match.away_score)

        dialog.update_match_information()

        # Visa dialog
        if dialog.exec():
            if dialog.home:
                home_team_id = self.selected_team.id
                away_team_id = dialog.opponent_id
            else:
                home_team_id = dialog.opponent_id
                away_team_id = self.selected_team.id

            if self.soccer_model.match_exists(
                self.selected_season.id,
                home_team_id,
                away_team_id,
                exclude_match_id=match.id
            ):
                self.view.show_warning(
                    "Match finns redan", "Den matchen finns redan tillagd."
                )
                return

            self.soccer_model.update_match(
                match_id=match.id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                match_date=dialog.match_date,
                home_score=dialog.home_score,
                away_score=dialog.away_score
            )
            self.competition_model.sort_by_keys(
                self.selected_team_matches, "match_date", reverse=True)
            self.refresh_selected_team()

    def on_delete_match_button_clicked(self):
        """
            Tar bort den valda matchen.
        """
        if (
            not self.has_selected_season() or
            not self.has_selected_team() or
            self.selected_match is None
        ):
            return

        confirmed = self.view.ask_question(
            "Radera match",
            "Är du säker på att du vill radera matchen?"
        )

        if not confirmed:
            return

        self.competition_model.delete_match(self.selected_match.id)
        self.refresh_selected_team()

        self.selected_match = None
        self.view.edit_match_button.setEnabled(False)
        self.view.delete_match_button.setEnabled(False)

    def on_standings_table_team_selection_changed(self):
        """
            Hanterar ändrad markering i serietabellen.
        """
        row = self.view.standings_table.get_selected_row()

        if row < 0:
            self.selected_team = None
            self.view.add_match_button.setEnabled(False)
            self.view.clear_team_information()
            return

        if not self.selected_season:
            return

        # Hämta tabellen för aktuell säsong
        standings = self.get_standings()

        if row >= len(standings):
            return

        standing_row = standings[row]
        team_id = standing_row.team.id

        self.selected_team = None
        # Hitta motsvarande Team-objekt i cache
        for team in self.teams:
            if team.id == team_id:
                self.selected_team = team
                break
        if not self.has_selected_team():
            return

        # Uppdatera laginformation
        self.view.update_team_statistics(standing_row)

        # Hämta matcher för laget
        self.load_selected_team_matches()

        self.view.add_match_button.setEnabled(True)
        self.view.update_team_matches(self.selected_team_matches)

    def on_team_matches_table_selection_changed(self):
        """
            Hanterar ändrad markering av match.
        """
        row = self.view.team_matches_table.get_selected_row()

        if row < 0 or row >= len(self.selected_team_matches):
            self.selected_match = None
            self.view.edit_match_button.setEnabled(False)
            self.view.delete_match_button.setEnabled(False)
        else:
            self.view.edit_match_button.setEnabled(True)
            self.view.delete_match_button.setEnabled(True)
            self.selected_match = self.selected_team_matches[row]

    def refresh_selected_team(self):
        """
            Uppdaterar data om det valda laget.
        """
        if not self.has_selected_season() or not self.has_selected_team():
            return

        selected_team_id = self.selected_team.id

        # Uppdatera matcher för laget
        self.load_selected_team_matches()

        # Hämta aktuell serietabell.
        standings = self.get_standings()

        # Återställ valt lag och uppdatera aktuell statistik
        for row, standing in enumerate(standings):
            if standing.team.id == selected_team_id:
                self.view.standings_table.selectRow(row)

                # Använd Team-objektet från Standing
                self.selected_team = standing.team

                self.view.update_team_statistics(standing)
                break

        self.view.update_standings_table(standings)

    def get_standings(self):
        """
            Hämtar och returnerar serietabellen.
        """
        if not self.has_selected_season():
            return []

        return self.soccer_model.get_standings(
            teams=self.teams,
            matches=self.season_matches
        )

    def has_selected_competition(self):
        """
            Avgör om en tävling/liga är vald eller ej.
        """
        return self.selected_competition is not None

    def has_selected_season(self):
        """
            Avgör om en säsong är vald eller ej.
        """
        return self.selected_season is not None

    def has_selected_team(self):
        """
            Avgör om ett lag är valt eller ej.
        """
        return self.selected_team is not None

    def has_selected_match(self):
        """
            Avgör om en match är vald eller ej.
        """
        return self.selected_match is not None

    def clear_selected_team(self):
        """
            Rensar valt lag.
        """
        self.selected_team = None
        self.selected_team_matches = []
        self.view.update_team_matches([])
        self.view.delete_team_button.setEnabled(False)
        self.view.add_match_button.setEnabled(False)
