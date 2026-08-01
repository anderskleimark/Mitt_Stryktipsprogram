import locale

from models.domains import Competition, Season, SoccerMatch, Standing, Team
from mvc import Model

locale.setlocale(locale.LC_COLLATE, "sv_SE.UTF-8")


# Modell för att hantera tävlingar och säsonger.


class CompetitionModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion som hämtar och returnerar alla ligor i databasen.
    def get_all(self):
        return self.database.competition_repository.get_all_competitions()

    # Funktion för att skapa en ny tävling/liga.
    def add_competition(self, name, country):
        self.database.competition_repository.add_competition(name, country)

    # Funktion för att radera en tävling/liga.
    def delete(self, competition_id):
        self.database.competition_repository.delete_competition(competition_id)

    # Funktion för att skapa en ny säsong.
    def add_season(self, competition_id, start_year, end_year):
        self.database.season_repository.add_season(
            competition_id, start_year, end_year)

    # Funktion för att radera en säsong.
    def delete_season(self, season_id):
        self.database.season_repository.delete_season(season_id)
