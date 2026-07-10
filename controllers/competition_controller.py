from mvc import Controller, Model, View
from misc.add_competition_dialog import AddCompetitionDialog
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)


class CompetitionController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)

        # Ligor och lag
        self.competitions = []
        self.seasons = []

        self.current_row = None
        self.current_competition = None

        self.add_connections()
        self.load_competitions()

        # Initialt läge
        self.view.delete_competition_button.setEnabled(False)
        self.view.show_info_button.setEnabled(False)

    def add_connections(self):
        self.view.competition_table.itemSelectionChanged.connect(
            self.on_selection_changed)
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

    # Funktion som laddar alla ligor, som finns i databasen.
    def load_competitions(self):

        self.competitions = self.model.get_all()
        self.view.update_competition_table(self.competitions)

    # Funktion som triggas, om en annan tävling/liga väljs eller om användaren klickar utanför tabellen.
    def on_selection_changed(self):
        row = self.view.competition_table.get_selected_row()

        if 0 <= row < len(self.competitions):

            self.current_row = row
            self.current_competition = self.competitions[row]

        else:

            self.current_row = None
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

            except ValueError as e:

                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion som triggas, när användaren vill visa information om säsonger och lag för en viss liga.
    def on_show_info_button_clicked(self):

        if self.current_competition is None:
            return

        self.view.update_competition_info(self.current_competition)
        self.seasons = self.model.get_seasons(self.current_competition.id)
        self.view.update_season_table(self.seasons)

        self.view.season_table.clearSelection()
        self.view.update_team_table([])

        self.view.show_details()

    # Funktion som triggas, om användaren klickar på "radera".
    def on_delete_competition_button_clicked(self):

        if self.current_row is None:
            return

        competition_id = int(self.view.competition_table.item(
            self.current_row, 0).text())

        reply = QMessageBox.question(
            self.view,
            "Radera tävlingen/ligan",
            "Är du säker på att du vill radera tävlingen/ligan och alla dess data?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.model.delete(competition_id)
        self.load_competitions()
        self.view.delete_competition_button.setEnabled(False)

    # Funktion som triggas, när användaren går tillbaka till översikten.
    def on_back_to_overview_button_clicked(self):
        self.view.show_overview()

    # Funktion som triggas, när val av säsong förändras.
    def on_season_selection_changed(self):

        row = self.view.season_table.get_selected_row()

        if row < 0 or row >= len(self.seasons):
            return

        season = self.seasons[row]

        teams = self.model.get_teams(season.id)
        self.view.update_team_table(teams)

    def on_add_season_button_clicked(self):
        pass

    def on_delete_season_button_clicked(self):
        pass

    def on_add_team_button_clicked(self):
        pass

    def on_delete_team_button_clicked(self):
        pass
