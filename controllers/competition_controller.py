from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox

from misc.add_competition_dialog import AddCompetitionDialog
from misc.add_match_dialog import AddMatchDialog
from misc.add_season_dialog import AddSeasonDialog
from misc.add_team_dialog import AddTeamDialog
from mvc import Controller


class CompetitionController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)

        # Ligor, säsonger, matcher och lag
        self.competitions = []
        self.seasons = []
        self.teams = []
        self.team_matches = []

        self.current_competition = None
        self.current_season = None
        self.current_team = None
        self.current_team_match = None

        self.add_connections()
        self.load_competitions()

        # Initialt läge
        self.view.delete_competition_button.setEnabled(False)
        self.view.show_info_button.setEnabled(False)
        self.view.update_competition_table(self.competitions)

    def add_connections(self):
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

    # Funktion som laddar alla ligor, som finns i databasen.
    def load_competitions(self):
        self.competitions = self.model.get_all()

    # Funktion som laddar alla lag för aktuell säsong.
    def load_teams(self):
        if self.current_season is None:
            self.teams = []
            return

        self.teams = self.model.get_teams(self.current_season.id)

    # Funktion som laddar ett lags alla seriematcher för vald säsong.
    def load_team_matches(self):
        if self.current_season is None or self.current_team is None:
            self.team_matches = []
            return

        self.team_matches = self.model.get_team_matches(
            self.current_season.id,
            self.current_team.id
        )

    # Funktion som triggas, om en annan tävling/liga väljs eller om
    # användaren klickar utanför tabellen.
    def on_competition_selection_changed(self):
        row = self.view.competition_table.get_selected_row()

        if 0 <= row < len(self.competitions):
            self.current_competition = self.competitions[row]
        else:
            self.current_competition = None

        enabled = self.current_competition is not None

        self.view.delete_competition_button.setEnabled(enabled)
        self.view.show_info_button.setEnabled(enabled)

    # Funktion som triggas, när användaren trycker på knappen "lägg till".
    def on_add_competition_button_clicked(self):
        dialog = AddCompetitionDialog(self.view)

        if dialog.exec():
            try:
                self.model.create_competition(
                    dialog.competition_name, dialog.country)
                self.load_competitions()
                self.view.update_competition_table(self.competitions)

            except ValueError as e:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion som triggas, när användaren vill visa information
    # om säsonger och lag för en viss tävling/liga.
    def on_show_info_button_clicked(self):
        if self.current_competition is None:
            return

        self.view.update_competition_info(self.current_competition)
        self.seasons = self.model.get_seasons(self.current_competition.id)
        self.view.update_season_table(self.seasons)

        self.current_season = None
        self.view.season_table.clearSelection()
        self.view.update_team_table([])

        self.view.show_details()

    # Funktion som triggas, om användaren klickar på "radera".
    def on_delete_competition_button_clicked(self):
        if self.current_competition is None:
            return

        # Dialogruta.
        reply = QMessageBox.question(
            self.view,
            "Radera tävlingen/ligan",
            "Är du säker på att du vill radera tävlingen/ligan och alla dess data?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        # Radera inte tävlingen/ligan.
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Radering sker.
        self.model.delete(self.current_competition.id)
        self.load_competitions()
        self.view.delete_competition_button.setEnabled(False)
        self.view.update_competition_table(self.competitions)
        self.current_competition = None

    # Funktion som triggas, när användaren går tillbaka till översikten.
    def on_back_to_overview_button_clicked(self):
        self.view.show_overview()

    # Funktion som triggas, när val av säsong förändras.
    def on_season_selection_changed(self):
        # Vald rad.
        row = self.view.season_table.get_selected_row()

        if row < 0 or row >= len(self.seasons):
            self.current_season = None
            self.view.update_team_table([])
            return

        self.current_season = self.seasons[row]
        self.load_teams()
        self.view.update_team_table(self.teams)
        self.current_team = None
        self.team_matches = []
        self.view.update_team_matches([])

    # Funktion som körs, när en ny säsong läggs till.
    def on_add_season_button_clicked(self):
        # Ingen tävling/liga vald.
        if self.current_competition is None:
            return

        # Dialog för att lägga till en ny säsong.
        dialog = AddSeasonDialog(self.view)

        if dialog.exec():
            try:
                # Tillägg av säsong.
                self.model.create_season(
                    self.current_competition.id,
                    dialog.start_year,
                    dialog.end_year
                )

                # Säsonger.
                self.seasons = self.model.get_seasons(
                    self.current_competition.id
                )

                # Uppdatering av tabellen med säsongerna.
                self.view.update_season_table(
                    self.seasons
                )

            except ValueError as e:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion som körs, när användaren vill radera en säsong.
    def on_delete_season_button_clicked(self):
        # Ingen säsong är vald.
        if self.current_season is None:
            return

        reply = QMessageBox.question(self.view, "Radera säsong", "Vill du radera säsongen?",
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.Cancel)

        # Ingen radering.
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Radering sker.
        self.model.delete_season(self.current_season.id)
        self.seasons = self.model.get_seasons(self.current_competition.id)

        # Uppdatera vyn.
        self.view.update_season_table(self.seasons)
        self.view.update_team_table([])

    def on_add_team_button_clicked(self):
        if self.current_season is None:
            return

        dialog = AddTeamDialog(self.view)

        if dialog.exec():
            try:
                # Skapa laget om det inte finns
                team_id = self.model.create_team(
                    dialog.team_name
                )

                # Koppla laget till säsongen
                self.model.add_team_to_season(
                    self.current_season.id,
                    team_id
                )

                # Uppdatera tabellen
                self.load_teams()
                self.view.update_team_table(self.teams)

            except ValueError as e:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion för att radera ett lag.
    def on_delete_team_button_clicked(self):
        if self.current_season is None:
            return

        if self.current_team is None:
            return

        self.model.remove_team_from_season(
            self.current_season.id,
            self.current_team.id
        )

        self.load_teams()
        self.view.update_team_table(self.teams)
        self.current_team = None
        self.team_matches = []
        self.view.update_team_matches([])

    # Funktion som triggas om valt lag förändras.
    def on_season_table_team_selection_changed(self):
        row = self.view.team_table.get_selected_row()

        if row < 0 or row >= len(self.teams):
            self.current_team = None
            return

        self.current_team = self.teams[row]

    def on_show_standing_table_button_clicked(self):
        if self.current_season is None:
            return

        # Uppdatera serietabellen
        self.update_standings_table()
        self.view.show_standings()

    def on_back_to_details_button_clicked(self):
        self.view.clear()
        self.view.show_details()

    # Funktion som triggas, om användaren vill lägga till en seriematch för aktivt lag.
    def on_add_match_button_clicked(self):
        if self.current_team is None:
            return

        opponents = [
            team for team in self.teams
            if team.id != self.current_team.id
        ]

        dialog = AddMatchDialog(self.current_team, opponents, self.view)

        if dialog.exec():
            if dialog.home:
                home_team_id = self.current_team.id
                away_team_id = dialog.opponent_id
            else:
                home_team_id = dialog.opponent_id
                away_team_id = self.current_team.id

            if self.model.match_exists(
                self.current_season.id,
                home_team_id,
                away_team_id
            ):
                QMessageBox.warning(
                    self.view,
                    "Match finns redan",
                    "Den matchen finns redan tillagd."
                )
                return

            self.model.add_match(
                self.current_season.id,
                home_team_id,
                away_team_id,
                dialog.match_date,
                dialog.home_score,
                dialog.away_score
            )

            self.refresh_current_team()

    def on_edit_match_button_clicked(self):
        if (self.current_season is None or self.current_team is None
                or self.current_team_match is None):
            return

        match = self.current_team_match

        opponents = [
            team for team in self.teams
            if team.id != self.current_team.id
        ]

        dialog = AddMatchDialog(
            self.current_team,
            opponents,
            self.view
        )

        # Hemma/borta
        if match.home_team.id == self.current_team.id:
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
                home_team_id = self.current_team.id
                away_team_id = dialog.opponent_id
            else:
                home_team_id = dialog.opponent_id
                away_team_id = self.current_team.id

            if self.model.match_exists(
                self.current_season.id,
                home_team_id,
                away_team_id,
                exclude_match_id=match.id
            ):
                QMessageBox.warning(
                    self.view, "Match finns redan", "Den matchen finns redan tillagd.")
                return

            self.model.update_match(
                match.id,
                home_team_id,
                away_team_id,
                dialog.match_date,
                dialog.home_score,
                dialog.away_score
            )
            self.refresh_current_team()

    def on_delete_match_button_clicked(self):
        if (
            self.current_season is None or
            self.current_team is None or
            self.current_team_match is None
        ):
            return

        reply = QMessageBox.question(
            self.view,
            "Radera match",
            "Är du säker på att du vill radera matchen?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.model.delete_match(self.current_team_match.id)

        self.refresh_current_team()

        self.current_team_match = None
        self.view.edit_match_button.setEnabled(False)
        self.view.delete_match_button.setEnabled(False)

    def on_standings_table_team_selection_changed(self):
        row = self.view.standings_table.get_selected_row()

        if row < 0:
            self.current_team = None
            self.view.add_match_button.setEnabled(False)
            self.view.clear_team_information()
            return

        if self.current_season is None:
            return

        # Hämta tabellen för aktuell säsong
        standings = self.model.get_standings(self.current_season.id)

        if row >= len(standings):
            return

        standing_row = standings[row]
        team_id = standing_row.team_id

        self.current_team = None
        # Hitta motsvarande Team-objekt i cache
        for team in self.teams:
            if team.id == team_id:
                self.current_team = team
                break
        if self.current_team is None:
            return

        # Uppdatera laginformation
        self.view.update_team_statistics(standing_row)

        # Hämta matcher för laget
        self.load_team_matches()

        self.view.add_match_button.setEnabled(True)
        self.view.update_team_matches(self.team_matches)

    # Funktion som triggas, om användaren väljer en annan av det aktiva lagets seriematcher.
    def on_team_matches_table_selection_changed(self):
        row = self.view.team_matches_table.get_selected_row()

        if row < 0 or row >= len(self.team_matches):
            self.current_team_match = None
            self.view.edit_match_button.setEnabled(False)
            self.view.delete_match_button.setEnabled(False)
        else:
            self.view.edit_match_button.setEnabled(True)
            self.view.delete_match_button.setEnabled(True)
            self.current_team_match = self.team_matches[row]

    # Funktion som uppdaterar det aktuella lagets information efter
    # att en match har lagts till, ändrats eller tagits bort.
    def refresh_current_team(self):
        if self.current_season is None or self.current_team is None:
            return

        current_team_id = self.current_team.id

        # Uppdatera matcher
        self.load_team_matches()
        self.view.update_team_matches(self.team_matches)

        # Uppdatera serietabellen
        standings = self.update_standings_table()

        # Återställ valt lag i tabellen
        for row, standing in enumerate(standings):

            if standing.team_id != current_team_id:
                continue

            self.view.standings_table.selectRow(row)

            # Behåll Team-objektet
            for team in self.teams:
                if team.id == current_team_id:
                    self.current_team = team
                    break

            self.view.update_team_statistics(standing)
            break

    # Funktion som uppdaterar ställningen.
    def update_standings_table(self):
        if self.current_season is None:
            return []

        standings = self.model.get_standings(
            self.current_season.id
        )

        self.view.update_standings_table(standings)

        return standings
