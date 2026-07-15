from dataclasses import dataclass

from mvc import Model
from misc.country import Country

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


@dataclass
class Standing:
    team_id: int
    name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

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

    # Funktion för att få fram namnet på en tävling/liga för ett visst år.
    # Exempelvis Allsvenskan 2026 eller Premier League 2026/2027.
    def get_competition_name(self, competition, season=None, year=False):

        if competition is None:
            return ""

        name = (
            f"{Country.get_flag(competition.country)} "
            f"{competition.name}"
        )

        if year and season is not None:
            if season.start_year == season.end_year:
                name += f" {season.start_year}"
            else:
                name += f" {season.start_year}/{season.end_year}"

        return name

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

    # Funktion som returnerar alla lagets matcher under säsongen.
    def get_team_matches(self, season_id, team_id):
        return self.database.get_team_matches(season_id, team_id)

    # Funktion för att koppla ett lag till en säsong.
    def add_team_to_season(self, season_id, team_id):
        self.database.add_team_to_season(season_id, team_id)

    # Funktion för att ta bort ett lag från en säsong.
    def remove_team_from_season(self, season_id, team_id):
        self.database.remove_team_from_season(season_id, team_id)

    def get_standings(self, season_id):

        teams = self.database.get_teams(season_id)
        matches = self.database.get_matches_by_season(season_id)

        standings = {}

        # Skapa tom tabell för alla lag
        for team_id, name in teams:

            standings[team_id] = {
                "team_id": team_id,
                "name": name,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0
            }

        # Lägg till matchresultat
        for match in matches:

            home_id = match[0]
            away_id = match[1]

            home_score = match[2]
            away_score = match[3]

            # Hoppa över ospelade matcher
            if home_score is None or away_score is None:
                continue

            home = standings[home_id]
            away = standings[away_id]

            home["played"] += 1
            away["played"] += 1

            home["goals_for"] += home_score
            home["goals_against"] += away_score

            away["goals_for"] += away_score
            away["goals_against"] += home_score

            if home_score > away_score:

                home["wins"] += 1
                home["points"] += 3

                away["losses"] += 1

            elif away_score > home_score:

                away["wins"] += 1
                away["points"] += 3

                home["losses"] += 1

            else:

                home["draws"] += 1
                away["draws"] += 1

                home["points"] += 1
                away["points"] += 1

        # Skapa resultatlista
        result = []

        for team in standings.values():

            result.append(
                Standing(
                    team_id=team["team_id"],
                    name=team["name"],
                    played=team["played"],
                    wins=team["wins"],
                    draws=team["draws"],
                    losses=team["losses"],
                    goals_for=team["goals_for"],
                    goals_against=team["goals_against"],
                    points=team["points"]
                )
            )

        # Sortering
        result.sort(
            key=lambda x: (
                x.points,
                x.goals_for - x.goals_against,
                x.goals_for
            ),
            reverse=True
        )

        return result

    def add_match(self, season_id, home_team_id,
                  away_team_id, match_date, home_score, away_score):
        self.database.add_match(
            season_id, home_team_id,
            away_team_id, match_date, home_score, away_score)
