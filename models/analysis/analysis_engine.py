import math

from models.domains import MatchAnalysis


class AnalysisEngine:
    MIN_MATCHES = 5
    DEFAULT_ATTACK_DEFENCE_COEFFICIENTS = 1.0
    REGRESSION_MATCHES = 5
    FORM_MATCHES = 5
    WIN_SCORE = 3
    DRAW_SCORE = 1
    MAX_POISSON_GOALS = 5
    MIN_LAMBDA_VALUE = 0.1

    def analyze_match(self, data):
        # Attack och försvar.
        self.calculate_attack_coefficients(data)
        self.calculate_defence_coefficients(data)

        # Dagsform.
        self.calculate_recent_form(
            data.home_statistics,
            data.home_matches
        )
        self.calculate_recent_form(
            data.away_statistics,
            data.away_matches
        )

        # Förväntat antal mål.
        lambda_home, lambda_away = self.calculate_expected_goals(data)
        home_poisson = self.calculate_poisson_distribution(lambda_home)
        away_poisson = self.calculate_poisson_distribution(lambda_away)

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

    def regress_to_mean(
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

    def calculate_attack_coefficients(self, data):
        season = data.season_statistics
        home = data.home_statistics
        away = data.away_statistics

        # Hemmalagets anfall
        if (
            home.home_matches_played >= self.MIN_MATCHES
            and season.average_home_goals > 0
        ):
            adjusted_average = self.regress_to_mean(
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
            adjusted_average = self.regress_to_mean(
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

    def calculate_defence_coefficients(self, data):
        home = data.home_statistics
        away = data.away_statistics
        season = data.season_statistics

        # Hemmalagets försvar
        if (
            home.home_matches_played >= self.MIN_MATCHES
            and season.average_away_goals > 0
        ):
            adjusted_average = self.regress_to_mean(
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
            adjusted_average = self.regress_to_mean(
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

    def calculate_expected_goals(self, data):
        home = data.home_statistics
        away = data.away_statistics
        season = data.season_statistics

        lambda_home = (
            season.average_home_goals
            * home.home_attack_coefficient
            * away.away_defence_coefficient
            * home.form_factor
        )

        lambda_home = max(lambda_home, self.MIN_LAMBDA_VALUE)

        lambda_away = (
            season.average_away_goals
            * away.away_attack_coefficient
            * home.home_defence_coefficient
            * away.form_factor
        )

        lambda_away = max(lambda_away, self.MIN_LAMBDA_VALUE)

        return lambda_home, lambda_away

    def calculate_recent_form(self, statistics, matches):
        """
        Beräknar lagets form utifrån de senaste matcherna.

        Returnerar ett värde mellan 0.0 och 1.0.
        """

        if not matches:
            statistics.recent_form = 0.5
            return

        recent_matches = sorted(
            (
                match
                for match in matches
                if match.match_date is not None
            ),
            key=lambda match: match.match_date,
            reverse=True
        )[:self.FORM_MATCHES]

        points = 0

        for match in recent_matches:
            if match.home_team.id == statistics.team.id:
                goals_for = match.home_score
                goals_against = match.away_score
            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for > goals_against:
                points += self.WIN_SCORE
            elif goals_for == goals_against:
                points += self.DRAW_SCORE

        max_points = len(recent_matches) * self.WIN_SCORE

        if max_points:
            statistics.recent_form = points / max_points
        else:
            statistics.recent_form = 0.5

    def calculate_poisson_distribution(
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
            probability = (
                math.exp(-lambda_value)
                * lambda_value ** goals
                / math.factorial(goals)
            )

            probabilities.append(probability)

        # Sannolikheten för max_goals eller fler mål.
        probability_max_plus = 1 - sum(probabilities)

        probabilities.append(probability_max_plus)

        return probabilities
