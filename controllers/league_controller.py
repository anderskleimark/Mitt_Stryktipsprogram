from mvc import Controller, Model, View
from misc.add_league_dialog import AddLeagueDialog
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)


class LeagueController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)

        # Ligor och lag
        self.leagues = []
        self.seasons = []

        self.current_row = None
        self.current_league = None

        self.add_connections()
        self.load_leagues()

        # Initialt läge
        self.view.delete_league_button.setEnabled(False)
        self.view.show_info_button.setEnabled(False)

    def add_connections(self):
        self.view.league_table.itemSelectionChanged.connect(
            self.on_selection_changed)

        self.view.add_league_button.clicked.connect(
            self.on_add_league_button_clicked
        )

        self.view.delete_league_button.clicked.connect(
            self.on_delete_league_button_clicked
        )

        self.view.show_info_button.clicked.connect(
            self.on_show_info_button_clicked
        )

        self.view.back_to_overview_button.clicked.connect(
            self.on_back_to_overview_button_clicked
        )

        self.view.season_table.itemSelectionChanged.connect(
            self.on_season_selection_changed
        )

    # Funktion som laddar alla ligor, som finns i databasen.
    def load_leagues(self):

        self.leagues = self.model.get_all()
        self.view.update_league_table(self.leagues)

    # Funktion som triggas, om en annan liga väljs eller om användaren klickar utanför tabellen.
    def on_selection_changed(self):
        row = self.view.league_table.get_selected_row()

        if 0 <= row < len(self.leagues):

            self.current_row = row
            self.current_league = self.leagues[row]

        else:

            self.current_row = None
            self.current_league = None

        enabled = self.current_league is not None

        self.view.delete_league_button.setEnabled(enabled)
        self.view.show_info_button.setEnabled(enabled)

    # Funktion som triggas, när användaren trycker på knappen "ligor".
    def on_add_league_button_clicked(self):
        dialog = AddLeagueDialog(self.view)

        if dialog.exec():

            try:

                self.model.create_league(
                    dialog.league_name,
                    dialog.country
                )

                self.load_leagues()

            except ValueError as e:

                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion som triggas, när användaren vill visa information om säsonger och lag för en viss liga.
    def on_show_info_button_clicked(self):

        if self.current_league is None:
            return

        self.view.update_league_info(
            self.current_league
        )

        self.seasons = self.model.get_seasons(
            self.current_league.id
        )

        self.view.update_season_table(
            self.seasons
        )

        self.view.season_table.clearSelection()
        self.view.update_team_table([])

        self.view.show_details()

    # Funktion som triggas, om användaren klickar på "radera".
    def on_delete_league_button_clicked(self):

        if self.current_row is None:
            return

        league_id = int(self.view.league_table.item(
            self.current_row, 0).text())

        reply = QMessageBox.question(
            self.view,
            "Radera ligan",
            "Är du säker på att du vill radera ligan och alla dess data?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.model.delete(league_id)
        self.load_leagues()
        self.view.delete_league_button.setEnabled(False)

    # Funktion som triggas, när användaren går tillbaka till översikten.
    def on_back_to_overview_button_clicked(self):
        self.view.show_overview()

    # Funtkion som triggas, när valav säsong förändras.
    def on_season_selection_changed(self):

        row = self.view.season_table.get_selected_row()

        if row < 0 or row >= len(self.seasons):
            return

        season = self.seasons[row]

        teams = self.model.get_teams(
            season.id
        )

        self.view.update_team_table(
            teams
        )
