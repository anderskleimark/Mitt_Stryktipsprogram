import math

from models.domains import MatchAnalysis


class AnalysisEngine:
    MIN_MATCHES = 3
    DEFAULT_ATTACK_DEFENCE_COEFFICIENTS = 1.0
    REGRESSION_MATCHES = 8
    FORM_MATCHES = 5
    WIN_SCORE = 3
    DRAW_SCORE = 1
    MAX_POISSON_GOALS = 5
    MIN_LAMBDA_VALUE = 0.1
    MAX_LAMBDA_VALUE = 3.8
    FORM_FACTOR_BASE = 0.85
    FORM_FACTOR_RANGE = 0.30
    MIN_PROBABILITY = 0.0
    DEFAULT_RECENT_FORM = 0.5

    def analyze_match(self, data):
        # Attack och försvar.
        self._calculate_attack_coefficients(data)
        self._calculate_defence_coefficients(data)

        # Dagsform.
        self._calculate_recent_form(
            data.home_statistics,
            data.home_matches
        )
        self._calculate_recent_form(
            data.away_statistics,
            data.away_matches
        )

        # Förväntat antal mål.
        lambda_home = self._calculate_lambda_home(data)
        lambda_away = self._calculate_lambda_away(data)
        home_poisson = self._calculate_poisson_distribution(lambda_home)
        away_poisson = self._calculate_poisson_distribution(lambda_away)

        return MatchAnalysis(
            home_statistics=data.home_statistics,
            away_statistics=data.away_statistics,
            h2h_statistics=data.h2h_statistics,

            lambda_home=lambda_home,
            lambda_away=lambda_away,
            home_poisson=home_poisson,
            away_poisson=away_poisson,

            probability_1=0.0,
            probability_x=0.0,
            probability_2=0.0,

            probability_over_25=0.0,
            probability_under_25=0.0,

            probability_btts=0.0,

            score_matrix=[]
        )

    def _regress_to_mean(
        self,
        average,
        league_average,
        matches
    ):
        k = self.REGRESSION_MATCHES

        return (
            matches * average +
            k * league_average
        ) / (matches + k)

    def _get_form_factor(self, statistics):
        return (
            self.FORM_FACTOR_BASE +
            statistics.recent_form * self.FORM_FACTOR_RANGE
        )

    def _calculate_attack_coefficients(self, data):
        season = data.season_statistics
        home = data.home_statistics
        away = data.away_statistics

        # Hemmalagets anfall
        if (
            home.home_matches_played >= self.MIN_MATCHES
            and season.average_home_goals > 0
        ):
            adjusted_average = self._regress_to_mean(
                home.average_home_goals_for,
                season.average_home_goals,
                home.home_matches_played
            )

            home.home_attack_coefficient = (
                adjusted_average / season.average_home_goals
            )
        else:
            home.home_attack_coefficient = self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS

        # Bortalagets anfall
        if (
            away.away_matches_played >= self.MIN_MATCHES
            and season.average_away_goals > 0
        ):
            adjusted_average = self._regress_to_mean(
                away.average_away_goals_for,
                season.average_away_goals,
                away.away_matches_played
            )

            away.away_attack_coefficient = (
                adjusted_average /
                season.average_away_goals
            )
        else:
            away.away_attack_coefficient = self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS

    def _calculate_defence_coefficients(self, data):
        home = data.home_statistics
        away = data.away_statistics
        season = data.season_statistics

        # Hemmalagets försvar
        if (
            home.home_matches_played >= self.MIN_MATCHES
            and season.average_away_goals > 0
        ):
            adjusted_average = self._regress_to_mean(
                home.average_home_goals_against,
                season.average_away_goals,
                home.home_matches_played
            )

            home.home_defence_coefficient = (
                adjusted_average / season.average_away_goals
            )
        else:
            home.home_defence_coefficient = self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS

        # Bortalagets försvar
        if (
            away.away_matches_played >= self.MIN_MATCHES
            and season.average_home_goals > 0
        ):
            adjusted_average = self._regress_to_mean(
                away.average_away_goals_against,
                season.average_home_goals,
                away.away_matches_played
            )

            away.away_defence_coefficient = (
                adjusted_average /
                season.average_home_goals
            )

        else:
            away.away_defence_coefficient = (
                self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
            )

    def _calculate_lambda_home(self, data):
        home = data.home_statistics
        away = data.away_statistics
        season = data.season_statistics

        form_factor = self._get_form_factor(home)

        lambda_home = (
            season.average_home_goals
            * home.home_attack_coefficient
            * away.away_defence_coefficient
            * form_factor
        )

        # Begränsa λ
        lambda_home = min(
            max(lambda_home, self.MIN_LAMBDA_VALUE),
            self.MAX_LAMBDA_VALUE
        )

        return lambda_home

    def _calculate_lambda_away(self, data):
        home = data.home_statistics
        away = data.away_statistics
        season = data.season_statistics

        form_factor = self._get_form_factor(away)

        lambda_away = (
            season.average_away_goals
            * away.away_attack_coefficient
            * home.home_defence_coefficient
            * form_factor
        )

        # Begränsa λ
        lambda_away = min(
            max(lambda_away, self.MIN_LAMBDA_VALUE),
            self.MAX_LAMBDA_VALUE
        )

        return lambda_away

    def _calculate_recent_form(
        self,
        statistics,
        matches
    ):
        """
        Beräknar lagets senaste form.
        """
        form_points = 0
        played_matches = 0

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            if match.home_team.id == statistics.team.id:
                goals_for = match.home_score
                goals_against = match.away_score
            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for > goals_against:
                form_points += 3

            elif goals_for == goals_against:
                form_points += 1

            played_matches += 1

        if played_matches == 0:
            statistics.recent_form = 0.0
            return

        statistics.recent_form = (
            form_points
            / (
                played_matches * 3
            )
        )

    def _calculate_poisson_distribution(
        self,
        lambda_value,
        max_goals=None
    ):
        """
        Beräknar sannolikheten för antal mål
        enligt Poissonfördelningen.

        Returnerar en lista där sista elementet
        är sannolikheten för max_goals eller fler mål.
        """

        if max_goals is None:
            max_goals = self.MAX_POISSON_GOALS

        probabilities = []

        # Beräkna sannolikheten för 0 till max_goals - 1 mål.
        for goals in range(max_goals):
            probability = max((
                math.exp(-lambda_value)
                * lambda_value ** goals
                / math.factorial(goals)
            ), self.MIN_PROBABILITY)

            probabilities.append(probability)

        # Sannolikheten för max_goals eller fler mål.
        probability_max_plus = 1 - sum(probabilities)

        probabilities.append(probability_max_plus)

        return probabilities
