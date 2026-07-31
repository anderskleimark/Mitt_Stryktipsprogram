from mvc import Model
from database.repositories.team_repository import TeamRepository
from database.repositories.country_repository import CountryRepository
from models.domains import Country, Team


class TeamModel(Model):
    """
        Modell för hantering av fotbollslag.
        Klassen ansvarar för att förmedla data mellan controller
        och repository.
    """

    def __init__(self, database):
        """
            Initierar modellen med en databasanslutning.
        """
        super().__init__()
        self.database = database

    def get_all(self):
        """
            Hämtar alla lag.
            Returnerar en lista med Team-objekt.
        """
        return self.database.team_repository.get_teams()

    def get_teams_by_country(self, country_id):
        """
            Hämtar alla lag för ett specifikt land.
            Returnerar en lista med Team-objekt.
        """
        return self.database.team_repository.get_teams(country_id)

    def add_team(
        self,
        country_id,
        team_name,
        display_name
    ):
        """
            Lägger till ett nytt lag.
        """
        self.database.team_repository.add_team(
            country_id=country_id,
            team_name=team_name,
            display_name=display_name
        )

    def update_team(
        self,
        team_id,
        country_id,
        team_name,
        display_name
    ):
        """
            Uppdaterar information om ett befintligt lag.
        """
        self.database.team_repository.update_team(
            team_id=team_id,
            country_id=country_id,
            team_name=team_name,
            display_name=display_name
        )

    def delete_team(self, team_id):
        """
            Tar bort ett lag.
        """
        self.database.team_repository.delete_team(
            team_id
        )
