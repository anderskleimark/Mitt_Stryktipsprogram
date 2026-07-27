from mvc import Model
from models.analysis.analysis_engine import AnalysisEngine
from models.domains import (
    AnalysisData,
    Competition,
    HeadToHeadStatistics,
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

    def create_team_statistics(self, team, season, matches):
        statistics = TeamStatistics(
            team=team,
            season=season
        )

        statistics.matches_played = len(matches)

        for match in matches:
            home_score = match.home_score or 0
            away_score = match.away_score or 0

            if match.home_team.id == team.id:
                # Hemmastatistik
                goals_for = home_score
                goals_against = away_score

                statistics.home_matches_played += 1

                statistics.home_goals_for += goals_for
                statistics.home_goals_against += goals_against

                if goals_for > goals_against:
                    statistics.home_wins += 1
                elif goals_for == goals_against:
                    statistics.home_draws += 1
                else:
                    statistics.home_losses += 1

            else:
                # Bortastatistik
                goals_for = away_score
                goals_against = home_score

                statistics.away_matches_played += 1

                statistics.away_goals_for += goals_for
                statistics.away_goals_against += goals_against

                if goals_for > goals_against:
                    statistics.away_wins += 1
                elif goals_for == goals_against:
                    statistics.away_draws += 1
                else:
                    statistics.away_losses += 1

            # Total statistik
            statistics.goals_for += goals_for
            statistics.goals_against += goals_against

            if goals_for > goals_against:
                statistics.wins += 1

            elif goals_for == goals_against:
                statistics.draws += 1

            else:
                statistics.losses += 1

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
            season,
            home_matches
        )

        away_statistics = self.create_team_statistics(
            away_team,
            season,
            away_matches
        )

        h2h_statistics = self.get_head_to_head_statistics(
            home_team.id, away_team.id)

        data = AnalysisData(
            season=season,
            home_team=home_team,
            away_team=away_team,
            home_matches=home_matches,
            away_matches=away_matches,
            season_statistics=season_statistics,
            home_statistics=home_statistics,
            away_statistics=away_statistics,
            h2h_statistics=h2h_statistics
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

    def get_head_to_head_statistics(
        self,
        team_id,
        opponent_id
    ):
        matches = self.soccer_model.get_head_to_head_matches(
            team_id,
            opponent_id
        )

        home_wins = 0
        home_draws = 0
        home_losses = 0

        home_goals = 0
        opponent_goals = 0

        for match in matches:

            if match.home_team.id == team_id:
                team_goals = match.home_score
                opp_goals = match.away_score

            else:
                team_goals = match.away_score
                opp_goals = match.home_score

            home_goals += team_goals
            opponent_goals += opp_goals

            if team_goals > opp_goals:
                home_wins += 1

            elif team_goals == opp_goals:
                home_draws += 1

            else:
                home_losses += 1

        return HeadToHeadStatistics(
            matches=len(matches),

            home_wins=home_wins,
            home_draws=home_draws,
            home_losses=home_losses,
            home_score=f"{home_goals} – {opponent_goals}",

            away_wins=home_losses,
            away_draws=home_draws,
            away_losses=home_wins,
            away_score=f"{opponent_goals} – {home_goals}"
        )
