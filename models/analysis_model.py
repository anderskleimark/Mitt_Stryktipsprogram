from models.analysis.analysis_engine import AnalysisEngine
from models.domains import AnalysisData, HeadToHeadStatistics, TeamStatistics
from datetime import date
from dateutil.relativedelta import relativedelta
from mvc import Model


class AnalysisModel(Model):
    """
        Modell som hämtar och förbereder data
        för matchanalys.
    """
    MODEL_HISTORY_YEARS = 3

    def __init__(self, database, soccer_model):
        super().__init__()

        self.database = database
        self.soccer_model = soccer_model
        self.engine = AnalysisEngine()

    def create_team_statistics(
        self,
        team,
        season,
        matches
    ):
        """
            Skapar statistik för ett lag
            utifrån angivna matcher.
        """
        statistics = TeamStatistics(
            team=team,
            season=season
        )

        statistics.matches_played = 0

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            statistics.matches_played += 1

            home_score = match.home_score
            away_score = match.away_score

            if match.home_team.id == team.id:
                goals_for = home_score
                goals_against = away_score

                statistics.home_matches_played += 1

                statistics.home_goals_for += (
                    goals_for
                )

                statistics.home_goals_against += (
                    goals_against
                )

                if goals_for > goals_against:
                    statistics.home_wins += 1

                elif goals_for == goals_against:
                    statistics.home_draws += 1

                else:
                    statistics.home_losses += 1

            else:
                goals_for = away_score
                goals_against = home_score

                statistics.away_matches_played += 1

                statistics.away_goals_for += (
                    goals_for
                )

                statistics.away_goals_against += (
                    goals_against
                )

                if goals_for > goals_against:
                    statistics.away_wins += 1

                elif goals_for == goals_against:
                    statistics.away_draws += 1

                else:
                    statistics.away_losses += 1

            statistics.goals_for += (
                goals_for
            )

            statistics.goals_against += (
                goals_against
            )

            if goals_for > goals_against:
                statistics.wins += 1

            elif goals_for == goals_against:
                statistics.draws += 1

            else:
                statistics.losses += 1

        return statistics

    def create_season_team_statistics(
        self,
        season
    ):
        """
            Skapar statistik för samtliga lag
            i den valda säsongen.
        """
        teams = (
            self.soccer_model.get_teams_in_season(
                season.id
            )
        )

        statistics = {}

        for team in teams:
            matches = self.soccer_model.get_matches(
                season.id,
                team.id
            )

            statistics[team.id] = (
                self.create_team_statistics(
                    team,
                    season,
                    matches
                )
            )

        return statistics

    def analyze_match(
        self,
        season,
        home_team,
        away_team
    ):
        """
            Hämtar och förbereder all data
            som behövs för matchanalysen.
        """
        # Datumintervall för modellens historik.
        reference_date = date.today()

        start_date = reference_date - relativedelta(
            years=self.MODEL_HISTORY_YEARS
        )

        # Matcher för respektive lag
        # under aktuell säsong.
        home_matches = self.soccer_model.get_matches(
            season.id,
            home_team.id
        )

        away_matches = self.soccer_model.get_matches(
            season.id,
            away_team.id
        )

        # Samtliga matcher i aktuell säsong.
        season_matches = self.soccer_model.get_matches(
            season.id
        )

        # Historiska matcher i aktuell liga.
        league_model_matches = (
            self.soccer_model
            .get_competition_matches_between_dates(
                season.competition.id,
                start_date,
                reference_date
            )
        )

        # Historiska matcher för hemmalaget,
        # oavsett liga.
        home_model_matches = (
            self.soccer_model
            .get_team_matches_between_dates(
                home_team.id,
                start_date,
                reference_date
            )
        )

        # Historiska matcher för bortalaget,
        # oavsett liga.
        away_model_matches = (
            self.soccer_model
            .get_team_matches_between_dates(
                away_team.id,
                start_date,
                reference_date
            )
        )

        team_model_matches = {
            home_team.id: home_model_matches,
            away_team.id: away_model_matches
        }

        # Statistik för aktuell säsong.
        season_statistics = (
            self.get_season_statistics(
                season.id
            )
        )

        # Statistik för samtliga lag
        # i aktuell säsong.
        season_team_statistics = (
            self.create_season_team_statistics(
                season
            )
        )

        home_statistics = (
            season_team_statistics[
                home_team.id
            ]
        )

        away_statistics = (
            season_team_statistics[
                away_team.id
            ]
        )

        # Inbördes möten.
        h2h_statistics = (
            self.get_head_to_head_statistics(
                home_team.id,
                away_team.id
            )
        )

        data = AnalysisData(
            season=season,
            home_team=home_team,
            away_team=away_team,

            reference_date=reference_date,

            home_matches=home_matches,
            away_matches=away_matches,
            season_matches=season_matches,

            league_model_matches=league_model_matches,
            team_model_matches=team_model_matches,

            season_statistics=season_statistics,
            season_team_statistics=(
                season_team_statistics
            ),

            home_statistics=home_statistics,
            away_statistics=away_statistics,

            h2h_statistics=h2h_statistics
        )

        return self.engine.analyze_match(
            data
        )

    def get_season_statistics(
        self,
        season_id
    ):
        """
            Hämtar statistik för en säsong.
        """
        return (
            self.database
            .season_repository
            .get_season_statistics(
                season_id
            )
        )

    def get_head_to_head_statistics(
        self,
        team_id,
        opponent_id
    ):
        """
            Beräknar statistik för inbördes möten.
        """
        matches = (
            self.soccer_model
            .get_head_to_head_matches(
                team_id,
                opponent_id
            )
        )

        home_wins = 0
        home_draws = 0
        home_losses = 0

        home_goals = 0
        opponent_goals = 0

        played_matches = 0

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            played_matches += 1

            if match.home_team.id == team_id:
                team_goals = (
                    match.home_score
                )

                opponent_match_goals = (
                    match.away_score
                )

            else:
                team_goals = (
                    match.away_score
                )

                opponent_match_goals = (
                    match.home_score
                )

            home_goals += (
                team_goals
            )

            opponent_goals += (
                opponent_match_goals
            )

            if (
                team_goals
                > opponent_match_goals
            ):
                home_wins += 1

            elif (
                team_goals
                == opponent_match_goals
            ):
                home_draws += 1

            else:
                home_losses += 1

        return HeadToHeadStatistics(
            matches=played_matches,

            home_wins=home_wins,
            home_draws=home_draws,
            home_losses=home_losses,

            home_score=(
                f"{home_goals} – "
                f"{opponent_goals}"
            ),

            away_wins=home_losses,
            away_draws=home_draws,
            away_losses=home_wins,

            away_score=(
                f"{opponent_goals} – "
                f"{home_goals}"
            )
        )
