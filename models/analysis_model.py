from mvc import Model
from models.analysis.analysis_engine import AnalysisEngine
from models.domains import (
    AnalysisData,
    Competition,
    SeasonStatistics,
    Season,
    SoccerMatch,
    Team,
    TeamStatistics
)


class AnalysisModel(Model):
    DEFAULT_ZERO = 0

    def __init__(self, database, soccer_model):
        super().__init__()

        self.database = database
        self.soccer_model = soccer_model
        self.engine = AnalysisEngine()

    def create_team_statistics(self, team, matches):
        statistics = TeamStatistics(
            team=team
        )

        # Antal matcher.
        statistics.matches_played += len(matches)

        for match in matches:
            # Är laget hemmalag?
            if match.home_team.id == team.id:
                statistics.home_matches += 1

                goals_for = match.home_score
                goals_against = match.away_score

                statistics.home_goals_for += goals_for
                statistics.home_goals_against += goals_against

            # Är laget bortalag?
            else:
                statistics.away_matches += 1

                goals_for = match.away_score
                goals_against = match.home_score

                statistics.away_goals_for += goals_for
                statistics.away_goals_against += goals_against

            statistics.goals_for += goals_for
            statistics.goals_against += goals_against

            # Resultat
            if goals_for > goals_against:
                statistics.wins += 1

            elif goals_for == goals_against:
                statistics.draws += 1

            else:
                statistics.losses += 1

        # Genomsnitt
        if statistics.matches_played > 0:
            statistics.average_goals_for = (
                statistics.goals_for /
                statistics.matches_played
            )

            statistics.average_goals_against = (
                statistics.goals_against /
                statistics.matches_played
            )

        if statistics.home_matches > 0:
            statistics.average_home_goals_for = (
                statistics.home_goals_for /
                statistics.home_matches
            )

            statistics.average_home_goals_against = (
                statistics.home_goals_against /
                statistics.home_matches
            )

        if statistics.away_matches > 0:
            statistics.average_away_goals_for = (
                statistics.away_goals_for /
                statistics.away_matches
            )

            statistics.average_away_goals_against = (
                statistics.away_goals_against /
                statistics.away_matches
            )

        return statistics

    def analyze_match(
        self,
        season,
        home_team,
        away_team
    ):
        # Hämta matcher
        home_matches = self.soccer_model.get_team_matches(
            season.id,
            home_team.id
        )

        away_matches = self.soccer_model.get_team_matches(
            season.id,
            away_team.id
        )

        # Hämta statistik om säsongen.
        season_statistics = self.get_season_statistics(season.id)

        home_statistics = self.create_team_statistics(
            home_team,
            home_matches
        )

        away_statistics = self.create_team_statistics(
            away_team,
            away_matches
        )

        data = AnalysisData(
            season=season,
            home_team=home_team,
            away_team=away_team,
            home_matches=home_matches,
            away_matches=away_matches,
            season_statistics=season_statistics,
            home_statistics=home_statistics,
            away_statistics=away_statistics
        )

        return self.engine.analyze_match(data)

    def get_season_statistics(self, season_id):
        row = (
            self.database.get_season_statistics(
                season_id
            )
        )
        if row is None:
            return SeasonStatistics()

        return SeasonStatistics(
            matches_played=row["matches_played"] or self.DEFAULT_ZERO,
            total_home_goals=row["total_home_goals"] or self.DEFAULT_ZERO,
            total_away_goals=row["total_away_goals"] or self.DEFAULT_ZERO
        )
