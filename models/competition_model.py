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
        rows = self.database.competition_repository.get_all_competitions()
        competitions = []

        for row in rows:
            competitions.append(
                Competition(
                    row["id"],
                    row["name"],
                    row["country"]
                )
            )
        return competitions

    # Funktion för att skapa en ny tävling/liga.
    def create_competition(self, name, country):
        self.database.competition_repository.create_competition(name, country)

    # Funktion för att radera en tävling/liga.
    def delete(self, competition_id):
        self.database.competition_repository.delete_competition(competition_id)

    # Funktion för att skapa en ny säsong.
    def create_season(self, competition_id, start_year, end_year):
        self.database.season_repository.create_season(
            competition_id, start_year, end_year)

    # Funktion för att radera en säsong.
    def delete_season(self, season_id):
        self.database.season_repository.delete_season(season_id)
