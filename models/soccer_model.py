from models.domains import SoccerMatch, Standing, Team
from mvc import Model


class SoccerModel(Model):
    """
        Modell som hanterar fotbollsrelaterad data.

        Klassen fungerar som ett mellanlager mellan controllers
        och repositories. Den ansvarar för att hämta, skapa,
        uppdatera och ta bort data om lag, matcher, säsonger
        och serietabeller.
    """

    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_teams_in_season(self, season_id):
        """
            Hämtar alla lag som tillhör en viss säsong.
        """
        return self.database.team_repository.get_teams_in_season(season_id)

    def get_matches(self, season_id, team_id=None, venue="all"):
        """
            Hämtar matcher för ett lag i en viss säsong.
            Parametern venue kan användas för att begränsa
            resultatet till hemma-, borta- eller alla matcher.
        """
        return self.database.soccer_match_repository.get_matches(
            season_id, team_id, venue)

    def get_seasons(self, competition_id):
        """
            Hämtar alla säsonger för en viss tävling.
        """
        return self.database.season_repository.get_seasons(competition_id)

    def get_standings(
        self,
        *,
        teams: list["Team"],
        matches: list["SoccerMatch"]
    ):
        """
        Beräknar den aktuella serietabellen.

        Tar emot en lista med lag och en lista med matcher
        och returnerar en sorterad lista med Standing-objekt.
        """

        standings = {}

        # Skapa en tom tabell för alla lag
        for team in teams:
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

            home_id = match.home_team.id
            away_id = match.away_team.id

            # Hoppa över matcher där något lag saknas
            if home_id not in standings or away_id not in standings:
                continue

            home_score = match.home_score
            away_score = match.away_score

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

    def add_match(
        self,
        *,
        season_id,
        home_team_id,
        away_team_id,
        match_date,
        home_score,
        away_score
    ):
        """
            Lägger till en ny match.
        """
        self.database.soccer_match_repository.add_match(
            season_id=season_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            home_score=home_score,
            away_score=away_score
        )

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
        """
            Uppdaterar en befintlig match.
        """
        self.database.soccer_match_repository.update_match(
            match_id=match_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            home_score=home_score,
            away_score=away_score
        )

    def match_exists(self, season_id, home_team_id, away_team_id, exclude_match_id=None):
        """
            Kontrollerar om en match redan finns registrerad.

            exclude_match_id används vid redigering av en match
            för att ignorera den aktuella matchen.
        """
        return self.database.soccer_match_repository.match_exists(
            season_id=season_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            exclude_match_id=exclude_match_id
        )

    def add_team_to_season(self, season_id, team_id):
        """
            Kopplar ett lag till en säsong.
        """
        self.database.team_repository.add_team_to_season(season_id, team_id)

    def remove_team_from_season(self, season_id, team_id):
        """
            Tar bort kopplingen mellan ett lag och en säsong.
        """
        self.database.team_repository.remove_team_from_season(
            season_id, team_id)

    def get_available_teams(
        self,
        season_id,
        country_id
    ):
        """
            Hämtar alla lag som kan läggas till i säsongen.
        """
        return self.database.team_repository.get_available_teams(
            season_id,
            country_id
        )

    def get_head_to_head_matches(
            self,
            home_team_id,
            away_team_id
    ):
        """
            Hämtar alla tidigare matcher mellan två lag.
        """
        return self.database.soccer_match_repository.get_head_to_head_matches(
            home_team_id,
            away_team_id
        )
