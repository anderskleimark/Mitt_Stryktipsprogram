from mvc import Model
from database.repositories.team_repository import TeamRepository
from database.repositories.country_repository import CountryRepository
from models.domains import Country, Team


class TeamModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_all(self):
        return self.database.team_repository.get_teams()

    def get_all_countries(self):
        rows = self.database.country_repository.get_all_countries()
        countries = []
        for row in rows:
            country = Country(
                id=row["id"],
                country_name=row["country_name"],
                iso_code=row["iso_code"]
            )
            countries.append(country)
        return countries

    def create_team(
        self,
        country_id,
        team_name,
        display_name
    ):
        self.database.team_repository.create_team(
            country_id=country_id,
            team_name=team_name,
            display_name=display_name
        )
