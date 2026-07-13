from dataclasses import dataclass
from mvc import Model

# Klass som hanterar data om tävlingar/ligor.


@dataclass
class Competition:
    id: int
    name: str
    country: str

# Klass som hanterar data om säsonger.


@dataclass
class Season:
    id: int
    competition_id: int
    start_year: int
    end_year: int

# Klass som hanterar data om lag.


@dataclass
class Team:
    id: int
    name: str

# Klass (Model) som används för att hämta och hantera data om fotbollsligor.


class CompetitionModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion som hämtar och returnerar alla ligor i databasen.
    def get_all(self):

        rows = self.database.get_all_competitions()
        competitions = []

        for row in rows:

            competitions.append(
                Competition(
                    row[0],  # id
                    row[1],  # namn
                    row[2]  # land
                )
            )

        return competitions

    # Funktion för att skapa en ny tävling/liga.
    def create_competition(self, name, country):
        self.database.create_competition(name, country)

    # Funktion för att radera en tävling/liga.
    def delete(self, competition_id):
        self.database.delete_competition(competition_id)

    # Funktion som hämtar och returnerar alla säsonger
    # för en viss tävling/liga med hjälp av dess id.
    def get_seasons(self, competition_id):

        rows = self.database.get_seasons(competition_id)

        return [
            Season(
                row[0],  # id
                competition_id,
                row[1],  # startår
                row[2]  # slutår
            )
            for row in rows
        ]

    # Funktion för att skapa en ny säsong.
    def create_season(self, competition_id, start_year, end_year):
        self.database.create_season(competition_id, start_year, end_year)

    # Funktion för att radera en säsong.
    def delete_season(self, season_id):
        self.database.delete_season(season_id)

    # Funktion som hämtar alla lag som tillhör en viss säsong.
    def get_teams(self, season_id):

        rows = self.database.get_teams(season_id)

        return [
            Team(
                row[0],  # Lagets id
                row[1]  # Lagets namn
            )
            for row in rows
        ]

    # Funktion för att skapa ett nytt lag.
    def create_team(self, name):

        team_id = self.database.get_team_id(name)

        # Om laget redan finns, så returneras team_id
        if team_id is not None:
            return team_id

        return self.database.create_team(name)

    # Funktion för att koppla ett lag till en säsong.
    def add_team_to_season(self, season_id, team_id):

        self.database.add_team_to_season(season_id, team_id)

    # Funktion för att ta bort ett lag från en säsong.
    def remove_team_from_season(self, season_id, team_id):

        self.database.remove_team_from_season(season_id, team_id)
