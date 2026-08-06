from mvc import Controller
from misc.dialogs.add_team_dialog import AddTeamDialog


class TeamController(Controller):
    """
        Controller som hanterar kommunikation mellan
        TeamView och TeamModel.
    """

    def __init__(
        self,
        *,
        team_model,
        country_model,
        view
    ):
        """
            Initierar klassen och laddar grunddata.
        """
        super().__init__(view)
        self.team_model = team_model
        self.country_model = country_model

        self.countries = []
        self.selected_team = None
        self.teams = []

        self.add_connections()

    def on_show_view(self):
        """
            Uppdaterar lagvyn innan den visas.
        """
        self.load_countries()
        self.load_teams()

    def add_connections(self):
        """
            Kopplar vyernas signaler till controller-metoder.
        """
        self.view.add_team_button.clicked.connect(
            self.on_add_team_button_clicked)
        self.view.delete_team_button.clicked.connect(
            self.on_delete_team_button_clicked)
        self.view.edit_team_button.clicked.connect(
            self.on_edit_team_button_clicked)

        self.view.country_combo.currentIndexChanged.connect(
            self.on_country_changed
        )
        self.view.team_table.itemSelectionChanged.connect(
            self.on_team_selection_changed
        )

    def load_countries(self):
        """
            Hämtar alla länder och uppdaterar landväljaren.
        """
        self.countries = self.country_model.get_all_countries()
        self.view.update_country_combobox(self.countries)

    def load_teams(self, country_id=None):
        """
            Hämtar lag, eventuellt filtrerade på land,
            och visar dem i tabellen.
        """
        if country_id is None:
            self.teams = self.team_model.get_all()
        else:
            self.teams = self.team_model.get_teams_by_country(
                country_id
            )

        self.view.show_teams(self.teams)

    def on_add_team_button_clicked(self):
        """
            Öppnar en dialog för att lägga till ett nytt lag.
        """
        dialog = AddTeamDialog(
            countries=self.countries,
            parent=self.view
        )

        if dialog.exec():
            try:
                self.team_model.add_team(
                    dialog.country_id, dialog.team_name, dialog.display_name)
                self.load_teams(
                    self.view.country_combo.currentData()
                )
            except ValueError as e:
                self.view.show_warning_message(
                    "Fel",
                    str(e)
                )

    def on_edit_team_button_clicked(self):
        """
            Öppnar en dialog för att redigera valt lag.
        """
        dialog = AddTeamDialog(
            self.countries,
            self.selected_team,
            self.view
        )

        if dialog.exec():
            try:
                self.team_model.update_team(
                    self.selected_team.id,
                    dialog.country_id,
                    dialog.team_name,
                    dialog.display_name
                )

                self.load_teams(
                    self.view.country_combo.currentData()
                )

            except ValueError as e:
                self.view.show_warning_message(
                    "Fel",
                    str(e)
                )

    def on_delete_team_button_clicked(self):
        """
            Tar bort valt lag efter bekräftelse.
        """
        if self.selected_team is None:
            return

        if not self.view.ask_delete_confirmation(
            self.selected_team.team_name
        ):
            return

        try:
            self.team_model.delete_team(
                self.selected_team.id
            )

            self.load_teams(
                self.view.country_combo.currentData()
            )
            self.selected_team = None
            self.view.set_button_status(False)
            self.view.clear_selection()

        except ValueError as e:
            self.view.show_warning_message(
                "Fel",
                str(e)
            )

    def on_team_selection_changed(self):
        """
            Hanterar ändring av markerat lag i tabellen.
        """
        row = self.view.get_selected_team_row()

        if row is None:
            self.selected_team = None
            self.view.set_button_status(False)
            return

        self.selected_team = self.teams[row]
        self.view.set_button_status(True)

    def on_country_changed(self):
        """
            Filtrerar lag efter valt land.
        """
        country_id = (
            self.view.country_combo.currentData()
        )

        self.load_teams(country_id)
