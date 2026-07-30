from mvc import Controller
from models.team_model import TeamModel
from misc.add_team_dialog import AddTeamDialog


class TeamController(Controller):
    def __init__(self, team_model, view):
        super().__init__(view)
        self.team_model = team_model

        self.country = None
        self.countries = []
        self.team = None
        self.teams = []

        self.load_countries()
        self.load_teams()

        self.add_connections()

    def add_connections(self):
        self.view.add_team_button.clicked.connect(
            self.on_add_team_button_clicked)
        self.view.delete_team_button.clicked.connect(
            self.on_delete_team_button_clicked)
        self.view.country_combo.currentIndexChanged.connect(
            self.country_changed
        )

    def load_countries(self):
        self.countries = self.team_model.get_all_countries()
        self.view.update_country_combobox(self.countries)

    def load_teams(self):
        self.teams = self.team_model.get_all()
        self.view.show_teams(self.teams)

    def on_add_team_button_clicked(self):
        dialog = AddTeamDialog(
            self.countries,
            self.view
        )

        if dialog.exec():
            self.team_model.create_team(
                dialog.country_id, dialog.team_name, dialog.display_name)

    def on_delete_team_button_clicked(self):
        print("Ta bort lag klickad")

    def country_changed(self):
        country_id = (
            self.view.country_combo.currentData()
        )

        if country_id is None:
            self.teams = self.team_model.get_all_teams()
        else:
            self.teams = self.team_model.get_teams_by_country(
                country_id
            )

        self.view.show_teams(self.teams)
