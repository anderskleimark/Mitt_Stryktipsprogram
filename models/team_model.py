from mvc import Model
from database.repositories.team_repository import TeamRepository
from database.repositories.country_repository import CountryRepository
from domains import Country, Team


class TeamModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_all(country_name=""):
        if (country_name == ""):
            rows = self.database.team_repository.get_all_teams()
        else:
            rows = self.database.team_repository.get_teams_by_country(
                country_name)
        teams = []
        for row in rows:
            team = Team(
                id=row["id"],
                team_name=row["team_name"],
                display_name=row["display_name"]
            )
            teams.append(Team)
        return teams

    def get_all_countries(self):
        rows = self.database.country_repository.get_all_countries()
        countries = []
        for row in rows:
            country = Country(
                id=row["id"],
                country_name=row["country_name"],
                iso_code=row["iso_code"]
            )
