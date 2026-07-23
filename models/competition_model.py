import locale

from models.domains import Competition, Season, SoccerMatch, Standing, Team
from mvc import Model

locale.setlocale(locale.LC_COLLATE, "sv_SE.UTF-8")


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
                    row["id"],
                    row["name"],
                    row["country"]
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
                id=row["season_id"],
                competition=Competition(
                    id=row["competition_id"],
                    country=row["country"],
                    name=row["name"]
                ),
                start_year=row["start_year"],
                end_year=row["end_year"]
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
        teams = []

        for row in rows:
            teams.append(Team(
                row["id"],
                row["name"]
            ))

        Model.sort_by_keys(teams, "name")
        return teams

    # Funktion för att skapa ett nytt lag.
    def create_team(self, name):
        team_id = self.database.get_team_id(name)

        # Om laget redan finns, så returneras team_id
        if team_id is not None:
            return team_id

        return self.database.create_team(name)

    # Funktion som returnerar alla lagets matcher under säsongen.
    def get_team_matches(self, season_id, team_id):
        rows = self.database.get_team_matches(season_id, team_id)
        matches = []

        for row in rows:
            matches.append(
                SoccerMatch(
                    id=row["match_id"],
                    season=Season(
                        id=row["season_id"],
                        competition=Competition(
                            id=row["competition_id"],
                            name=row["competition_name"],
                            country=row["country"]
                        ),
                        start_year=row["start_year"],
                        end_year=row["end_year"]
                    ),
                    home_team=Team(
                        id=row["home_team_id"],
                        name=row["home_team_name"]
                    ),
                    away_team=Team(
                        id=row["away_team_id"],
                        name=row["away_team_name"]
                    ),
                    match_date=row["match_date"],
                    home_score=row["home_score"],
                    away_score=row["away_score"]
                )
            )
        return Model.sort_by_keys(matches, "match_date", reverse=True)

    # Funktion för att koppla ett lag till en säsong.
    def add_team_to_season(self, season_id, team_id):
        self.database.add_team_to_season(season_id, team_id)

    # Funktion för att ta bort ett lag från en säsong.
    def remove_team_from_season(self, season_id, team_id):
        self.database.remove_team_from_season(season_id, team_id)

    # Funktion för att hämta aktuell ställning för angiven säsong.
    def get_standings(self, season_id):
        teams = self.database.get_teams(season_id)
        matches = self.database.get_matches_by_season(season_id)

        standings = {}

        # Skapa en tom tabell för alla lag
        for row in teams:
            team = Team(
                id=row["id"],
                name=row["name"]
            )

            standings[team.id] = Standing(
                team=team,
                played=0,
                wins=0,
                draws=0,
                losses=0,
                goals_for=0,
                goals_against=0,
                points=0
            )

        # Lägg till matchresultat
        for match in matches:
            home_id = match["home_team_id"]
            away_id = match["away_team_id"]

            home_score = match["home_score"]
            away_score = match["away_score"]

            # Hoppa över ospelade matcher
            if home_score is None or away_score is None:
                continue

            home = standings[home_id]
            away = standings[away_id]

            home.played += 1
            away.played += 1

            home.goals_for += home_score
            home.goals_against += away_score

            away.goals_for += away_score
            away.goals_against += home_score

            if home_score > away_score:
                home.wins += 1
                home.points += 3
                away.losses += 1

            elif away_score > home_score:
                away.wins += 1
                away.points += 3
                home.losses += 1

            else:
                home.draws += 1
                away.draws += 1

                home.points += 1
                away.points += 1

        # Gör om dictionaryn till en lista
        result = list(standings.values())

        # Sortera tabellen
        result.sort(
            key=lambda standing: (
                standing.points,
                standing.goals_for - standing.goals_against,
                standing.goals_for
            ),
            reverse=True
        )

        return result

    # Funktion för att lägga till en ny match i databasen.
    def add_match(self, season_id, home_team_id,
                  away_team_id, match_date, home_score, away_score):
        self.database.add_match(
            season_id, home_team_id,
            away_team_id, match_date, home_score, away_score)

    # Funktion för att uppdatera en seriematch.
    def update_match(
        self,
        *,
        match_id,
        home_team_id,
        away_team_id,
        match_date,
        home_score,
        away_score
    ):
        self.database.update_match(
            match_id, home_team_id, away_team_id, match_date, home_score, away_score)

    # Funktion som returnerar True om angiven match redan existerar.
    # Om inte, så returneras False.
    def match_exists(self, season_id, home_team_id, away_team_id, exclude_match_id=None):
        return self.database.match_exists(season_id, home_team_id, away_team_id, exclude_match_id)
