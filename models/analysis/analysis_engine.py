import math

from models.domains import MatchAnalysis


class AnalysisEngine:
    """
        Klass som genomför statistisk analys av en fotbollsmatch.
    """

    # --------------------------------------------------
    # Grundinställningar
    # --------------------------------------------------

    MIN_MATCHES = 3
    DEFAULT_ATTACK_DEFENCE_COEFFICIENTS = 1.0

    REGRESSION_MATCHES = 8

    FORM_MATCHES = 5
    WIN_SCORE = 3
    DRAW_SCORE = 1

    # --------------------------------------------------
    # Poisson / Dixon-Coles
    # --------------------------------------------------

    MAX_POISSON_GOALS = 5
    MAX_SCORE_MATRIX_GOALS = 10

    MIN_LAMBDA_VALUE = 0.1
    MAX_LAMBDA_VALUE = 3.8

    MIN_PROBABILITY = 0.0

    RHO_MIN = -0.30
    RHO_MAX = 0.30
    RHO_STEP = 0.001

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    FORM_FACTOR_BASE = 0.85
    FORM_FACTOR_RANGE = 0.30

    DEFAULT_RECENT_FORM = 0.5

    # --------------------------------------------------
    # De mest sannolika resultaten
    # --------------------------------------------------

    NUMBER_OF_RESULTS = 5

    def analyze_match(
        self,
        data
    ):
        """
            Analyserar en fotbollsmatch.
        """

        # Förbered statistik för samtliga lag.
        self._prepare_season_team_statistics(
            data
        )

        # Förväntat antal mål.
        lambda_home = self._calculate_lambda_home(
            data.season_statistics,
            data.home_statistics,
            data.away_statistics
        )

        lambda_away = self._calculate_lambda_away(
            data.season_statistics,
            data.home_statistics,
            data.away_statistics
        )

        # Marginala Poissonfördelningar.
        home_poisson = self._calculate_poisson_distribution(
            lambda_home
        )

        away_poisson = self._calculate_poisson_distribution(
            lambda_away
        )

        # Skatta Dixon-Coles rho.
        rho = self._estimate_rho(
            data
        )

        # Dixon-Coles-korrigerad resultatmatris.
        score_matrix = self._calculate_score_matrix(
            lambda_home,
            lambda_away,
            rho
        )
        # De mest sannolika resultaten
        most_likely_scores = (
            self._get_most_likely_scores(
                score_matrix
            )
        )

        (
            probability_1,
            probability_x,
            probability_2
        ) = self._calculate_match_probabilities(
            score_matrix
        )

        (
            probability_over_25,
            probability_under_25
        ) = self._calculate_over_under_probabilities(
            score_matrix
        )

        probability_btts = (
            self._calculate_btts_probability(
                score_matrix
            )
        )

        return MatchAnalysis(
            home_statistics=data.home_statistics,
            away_statistics=data.away_statistics,
            h2h_statistics=data.h2h_statistics,

            lambda_home=lambda_home,
            lambda_away=lambda_away,

            home_poisson=home_poisson,
            away_poisson=away_poisson,

            rho=rho,

            probability_1=probability_1,
            probability_x=probability_x,
            probability_2=probability_2,

            probability_over_25=probability_over_25,
            probability_under_25=probability_under_25,
            probability_btts=probability_btts,

            most_likely_scores=most_likely_scores,

            score_matrix=score_matrix
        )

    # --------------------------------------------------
    # Regression
    # --------------------------------------------------

    def _regress_to_mean(
        self,
        average,
        league_average,
        matches
    ):
        """
            Drar lagets snitt mot ligans genomsnitt
            när antalet matcher är begränsat.
        """
        k = self.REGRESSION_MATCHES

        return (
            matches * average
            + k * league_average
        ) / (
            matches + k
        )

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _get_form_factor(
        self,
        statistics
    ):
        """
            Returnerar formfaktor för laget.
        """
        return (
            self.FORM_FACTOR_BASE
            + statistics.recent_form
            * self.FORM_FACTOR_RANGE
        )

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

            if (
                match.home_team.id
                == statistics.team.id
            ):
                goals_for = match.home_score
                goals_against = match.away_score

            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for > goals_against:
                form_points += self.WIN_SCORE

            elif goals_for == goals_against:
                form_points += self.DRAW_SCORE

            played_matches += 1

        if played_matches == 0:
            statistics.recent_form = (
                self.DEFAULT_RECENT_FORM
            )
            return

        statistics.recent_form = (
            form_points
            / (
                played_matches
                * self.WIN_SCORE
            )
        )

    # --------------------------------------------------
    # Attack
    # --------------------------------------------------

    def _calculate_home_attack_coefficient(
        self,
        statistics,
        season_statistics
    ):
        """
            Beräknar lagets anfallskoefficient
            för hemmamatcher.
        """
        if (
            statistics.home_matches_played
            >= self.MIN_MATCHES
            and season_statistics.average_home_goals > 0
        ):
            adjusted_average = (
                self._regress_to_mean(
                    statistics.average_home_goals_for,
                    season_statistics.average_home_goals,
                    statistics.home_matches_played
                )
            )

            statistics.home_attack_coefficient = (
                adjusted_average
                / season_statistics.average_home_goals
            )

        else:
            statistics.home_attack_coefficient = (
                self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
            )

    def _calculate_away_attack_coefficient(
        self,
        statistics,
        season_statistics
    ):
        """
            Beräknar lagets anfallskoefficient
            för bortamatcher.
        """
        if (
            statistics.away_matches_played
            >= self.MIN_MATCHES
            and season_statistics.average_away_goals > 0
        ):
            adjusted_average = (
                self._regress_to_mean(
                    statistics.average_away_goals_for,
                    season_statistics.average_away_goals,
                    statistics.away_matches_played
                )
            )

            statistics.away_attack_coefficient = (
                adjusted_average
                / season_statistics.average_away_goals
            )

        else:
            statistics.away_attack_coefficient = (
                self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
            )

    # --------------------------------------------------
    # Försvar
    # --------------------------------------------------

    def _calculate_home_defence_coefficient(
        self,
        statistics,
        season_statistics
    ):
        """
            Beräknar lagets försvarskoefficient
            för hemmamatcher.
        """
        if (
            statistics.home_matches_played
            >= self.MIN_MATCHES
            and season_statistics.average_away_goals > 0
        ):
            adjusted_average = (
                self._regress_to_mean(
                    statistics.average_home_goals_against,
                    season_statistics.average_away_goals,
                    statistics.home_matches_played
                )
            )

            statistics.home_defence_coefficient = (
                adjusted_average
                / season_statistics.average_away_goals
            )

        else:
            statistics.home_defence_coefficient = (
                self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
            )

    def _calculate_away_defence_coefficient(
        self,
        statistics,
        season_statistics
    ):
        """
            Beräknar lagets försvarskoefficient
            för bortamatcher.
        """
        if (
            statistics.away_matches_played
            >= self.MIN_MATCHES
            and season_statistics.average_home_goals > 0
        ):
            adjusted_average = (
                self._regress_to_mean(
                    statistics.average_away_goals_against,
                    season_statistics.average_home_goals,
                    statistics.away_matches_played
                )
            )

            statistics.away_defence_coefficient = (
                adjusted_average
                / season_statistics.average_home_goals
            )

        else:
            statistics.away_defence_coefficient = (
                self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
            )

    def _calculate_team_coefficients(
        self,
        statistics,
        season_statistics
    ):
        """
            Beräknar lagets attack- och
            försvarskoefficienter.
        """
        self._calculate_home_attack_coefficient(
            statistics,
            season_statistics
        )

        self._calculate_away_attack_coefficient(
            statistics,
            season_statistics
        )

        self._calculate_home_defence_coefficient(
            statistics,
            season_statistics
        )

        self._calculate_away_defence_coefficient(
            statistics,
            season_statistics
        )

    # --------------------------------------------------
    # Säsongsförberedelse
    # --------------------------------------------------

    def _get_team_matches(
        self,
        matches,
        team_id
    ):
        """
            Returnerar matcher för angivet lag.
        """
        return [
            match
            for match in matches
            if team_id in (
                match.home_team.id,
                match.away_team.id
            )
        ]

    def _prepare_season_team_statistics(
        self,
        data
    ):
        """
            Beräknar koefficienter och form
            för samtliga lag i säsongen.
        """
        for statistics in (
            data.season_team_statistics.values()
        ):
            self._calculate_team_coefficients(
                statistics,
                data.season_statistics
            )

            matches = self._get_team_matches(
                data.season_matches,
                statistics.team.id
            )

            self._calculate_recent_form(
                statistics,
                matches
            )

    # --------------------------------------------------
    # Lambda
    # --------------------------------------------------

    def _calculate_lambda_home(
        self,
        season_statistics,
        home_statistics,
        away_statistics
    ):
        """
            Beräknar förväntat antal mål
            för hemmalaget.
        """
        form_factor = self._get_form_factor(
            home_statistics
        )

        lambda_home = (
            season_statistics.average_home_goals
            * home_statistics.home_attack_coefficient
            * away_statistics.away_defence_coefficient
            * form_factor
        )

        return min(
            max(
                lambda_home,
                self.MIN_LAMBDA_VALUE
            ),
            self.MAX_LAMBDA_VALUE
        )

    def _calculate_lambda_away(
        self,
        season_statistics,
        home_statistics,
        away_statistics
    ):
        """
            Beräknar förväntat antal mål
            för bortalaget.
        """
        form_factor = self._get_form_factor(
            away_statistics
        )

        lambda_away = (
            season_statistics.average_away_goals
            * away_statistics.away_attack_coefficient
            * home_statistics.home_defence_coefficient
            * form_factor
        )

        return min(
            max(
                lambda_away,
                self.MIN_LAMBDA_VALUE
            ),
            self.MAX_LAMBDA_VALUE
        )

    # --------------------------------------------------
    # Poisson
    # --------------------------------------------------

    def _calculate_poisson_probability(
        self,
        goals,
        lambda_value
    ):
        """
            Beräknar Poisson-sannolikheten
            för exakt antal mål.
        """
        return (
            math.exp(-lambda_value)
            * lambda_value ** goals
            / math.factorial(goals)
        )

    def _calculate_poisson_distribution(
        self,
        lambda_value,
        max_goals=None
    ):
        """
            Beräknar Poissonfördelningen för
            antal mål.

            Sista värdet motsvarar max_goals
            eller fler mål.
        """
        if max_goals is None:
            max_goals = self.MAX_POISSON_GOALS

        probabilities = []

        for goals in range(
            max_goals
        ):
            probability = (
                self._calculate_poisson_probability(
                    goals,
                    lambda_value
                )
            )

            probabilities.append(
                max(
                    probability,
                    self.MIN_PROBABILITY
                )
            )

        probability_max_plus = (
            1
            - sum(probabilities)
        )

        probabilities.append(
            probability_max_plus
        )

        return probabilities

    # --------------------------------------------------
    # Dixon-Coles
    # --------------------------------------------------

    def _calculate_dixon_coles_tau(
        self,
        home_goals,
        away_goals,
        lambda_home,
        lambda_away,
        rho
    ):
        """
            Beräknar Dixon-Coles-korrigeringen
            för ett matchresultat.
        """
        if (
            home_goals == 0
            and away_goals == 0
        ):
            return (
                1
                - lambda_home
                * lambda_away
                * rho
            )

        if (
            home_goals == 0
            and away_goals == 1
        ):
            return (
                1
                + lambda_home
                * rho
            )

        if (
            home_goals == 1
            and away_goals == 0
        ):
            return (
                1
                + lambda_away
                * rho
            )

        if (
            home_goals == 1
            and away_goals == 1
        ):
            return (
                1 - rho
            )

        return 1.0

    def _calculate_score_matrix(
        self,
        lambda_home,
        lambda_away,
        rho
    ):
        """
            Skapar Dixon-Coles-korrigerad
            resultatmatris.
        """
        matrix = []

        for home_goals in range(
            self.MAX_SCORE_MATRIX_GOALS + 1
        ):
            row = []

            for away_goals in range(
                self.MAX_SCORE_MATRIX_GOALS + 1
            ):
                home_probability = (
                    self._calculate_poisson_probability(
                        home_goals,
                        lambda_home
                    )
                )

                away_probability = (
                    self._calculate_poisson_probability(
                        away_goals,
                        lambda_away
                    )
                )

                tau = self._calculate_dixon_coles_tau(
                    home_goals,
                    away_goals,
                    lambda_home,
                    lambda_away,
                    rho
                )

                probability = (
                    home_probability
                    * away_probability
                    * tau
                )

                row.append(
                    probability
                )

            matrix.append(
                row
            )

        return matrix

    # --------------------------------------------------
    # Matchsannolikheter
    # --------------------------------------------------

    def _calculate_match_probabilities(
        self,
        score_matrix
    ):
        """
            Beräknar sannolikheterna för
            hemmaseger, oavgjort och bortaseger.
        """
        probability_1 = 0.0
        probability_x = 0.0
        probability_2 = 0.0

        for home_goals, row in enumerate(
            score_matrix
        ):
            for away_goals, probability in enumerate(
                row
            ):
                if home_goals > away_goals:
                    probability_1 += probability

                elif home_goals == away_goals:
                    probability_x += probability

                else:
                    probability_2 += probability

        return (
            probability_1,
            probability_x,
            probability_2
        )

    # --------------------------------------------------
    # Rho
    # --------------------------------------------------

    def _calculate_rho_log_likelihood(
        self,
        data,
        rho
    ):
        """
            Beräknar log-likelihood för ett
            givet Dixon-Coles-rho.
        """
        log_likelihood = 0.0

        for match in data.season_matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            home_statistics = (
                data.season_team_statistics.get(
                    match.home_team.id
                )
            )

            away_statistics = (
                data.season_team_statistics.get(
                    match.away_team.id
                )
            )

            if (
                home_statistics is None
                or away_statistics is None
            ):
                continue

            lambda_home = (
                self._calculate_lambda_home(
                    data.season_statistics,
                    home_statistics,
                    away_statistics
                )
            )

            lambda_away = (
                self._calculate_lambda_away(
                    data.season_statistics,
                    home_statistics,
                    away_statistics
                )
            )

            tau = self._calculate_dixon_coles_tau(
                match.home_score,
                match.away_score,
                lambda_home,
                lambda_away,
                rho
            )

            if tau <= 0:
                return float("-inf")

            log_likelihood += math.log(
                tau
            )

        return log_likelihood

    def _estimate_rho(
        self,
        data
    ):
        """
            Skattar Dixon-Coles rho genom att
            maximera log-likelihood för säsongens matcher.
        """
        best_rho = 0.0
        best_log_likelihood = float("-inf")

        rho = self.RHO_MIN

        while rho <= self.RHO_MAX:
            log_likelihood = (
                self._calculate_rho_log_likelihood(
                    data,
                    rho
                )
            )

            if (
                log_likelihood
                > best_log_likelihood
            ):
                best_log_likelihood = (
                    log_likelihood
                )

                best_rho = rho

            rho += self.RHO_STEP

        return best_rho

    def _calculate_over_under_probabilities(
        self,
        score_matrix
    ):
        """
            Beräknar sannolikheterna för
            över och under 2,5 mål.
        """
        probability_over_25 = 0.0
        probability_under_25 = 0.0

        for home_goals, row in enumerate(
            score_matrix
        ):
            for away_goals, probability in enumerate(
                row
            ):
                total_goals = (
                    home_goals
                    + away_goals
                )

                if total_goals > 2:
                    probability_over_25 += probability

                else:
                    probability_under_25 += probability

        return (
            probability_over_25,
            probability_under_25
        )

    def _calculate_btts_probability(
        self,
        score_matrix
    ):
        """
            Beräknar sannolikheten för att
            båda lagen gör mål.
        """
        probability_btts = 0.0

        for home_goals, row in enumerate(
            score_matrix
        ):
            for away_goals, probability in enumerate(
                row
            ):
                if (
                    home_goals > 0
                    and away_goals > 0
                ):
                    probability_btts += probability

        return probability_btts

    def _get_most_likely_scores(
        self,
        score_matrix,
        count=None
    ):
        """
            Returnerar de mest sannolika
            exakta matchresultaten.
        """
        if count is None:
            count = self.NUMBER_OF_RESULTS
        scores = []

        for home_goals, row in enumerate(
            score_matrix
        ):
            for away_goals, probability in enumerate(
                row
            ):
                scores.append(
                    (
                        home_goals,
                        away_goals,
                        probability
                    )
                )

        scores.sort(
            key=lambda score: score[2],
            reverse=True
        )

        return scores[:count]
