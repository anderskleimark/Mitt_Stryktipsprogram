from mvc import Controller, Model, View
from misc.add_league_dialog import AddLeagueDialog
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)


class LeagueController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()
        self.load_leagues()
        self.current_row = None
        self.view.delete_league_button.setEnabled(False)

    def add_connections(self):
        self.view.league_table.itemSelectionChanged.connect(
            self.on_selection_changed)
        self.view.add_league_button.clicked.connect(
            self.on_add_league_button_clicked)
        self.view.delete_league_button.clicked.connect(
            self.on_delete_league_button_clicked)

        self.view.league_table.selectionModel().selectionChanged.connect(
            self.on_league_selection_changed
        )

    # Funktion som laddar alla ligor, som finns i databasen.
    def load_leagues(self):

        leagues = self.model.get_all()
        self.view.update_league_table(leagues)

    # Funktion som triggas, om en annan liga väljs eller om användaren klickar utanför tabellen.
    def on_selection_changed(self):
        row = self.view.league_table.get_selected_row()

        if row >= 0:
            self.current_row = row

        else:
            self.current_row = None

        self.view.delete_league_button.setEnabled(True)

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

    # Funktion som triggas, om användaren klickar på "radera".
    def on_delete_league_button_clicked(self):

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

    # Funktion som triggas, om vald liga förändras.
    def on_league_selection_changed(self):
        self.current_row = self.view.league_table.get_selected_row()
        self.view.delete_league_button.setEnabled(self.current_row >= 0)
