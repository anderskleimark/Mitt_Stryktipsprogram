from models.domains import MatchAnalysis


class AnalysisEngine:
    MIN_MATCHES = 5
    DEFAULT_ATTACK_DEFENCE_COEFFICIENTS = 1.0
    REGRESSION_MATCHES = 5
    FORM_MATCHES = 5
    WIN_SCORE = 3
    DRAW_SCORE = 1

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

        return MatchAnalysis(
            home_statistics=data.home_statistics,
            away_statistics=data.away_statistics,

            lambda_home=lambda_home,
            lambda_away=lambda_away,

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
        )

        lambda_home = max(lambda_home, 0.1)

        lambda_away = (
            season.average_away_goals
            * away.away_attack_coefficient
            * home.home_defence_coefficient
        )

        lambda_away = max(lambda_away, 0.1)

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
