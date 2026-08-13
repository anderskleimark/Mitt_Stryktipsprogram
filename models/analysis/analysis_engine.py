import math

from models.domains import MatchAnalysis


class AnalysisEngine:
    """
        Klass som genomför statistisk analys
        av en fotbollsmatch.
    """

    # --------------------------------------------------
    # Grundinställningar
    # --------------------------------------------------

    DEFAULT_ATTACK_DEFENCE_COEFFICIENTS = 1.0

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

    TIME_DECAY = 0.003

    OTHER_COMPETITION_WEIGHT = 0.75

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    FORM_MATCHES = 5

    WIN_SCORE = 3
    DRAW_SCORE = 1

    FORM_FACTOR_BASE = 0.85
    FORM_FACTOR_RANGE = 0.30

    DEFAULT_RECENT_FORM = 0.5

    # --------------------------------------------------
    # De mest sannolika resultaten
    # --------------------------------------------------

    NUMBER_OF_RESULTS = 5

    # --------------------------------------------------
    # Analys
    # --------------------------------------------------

    def analyze_match(
        self,
        data
    ):
        """
            Analyserar en fotbollsmatch.
        """

        # --------------------------------------------------
        # Ligans historiska grundnivå
        # --------------------------------------------------

        (
            average_home_goals,
            average_away_goals
        ) = self._calculate_weighted_league_averages(
            data.league_model_matches,
            data.reference_date
        )

        # Fallback till aktuell säsong.
        if average_home_goals is None:
            average_home_goals = (
                data.season_statistics.average_home_goals
            )

        if average_away_goals is None:
            average_away_goals = (
                data.season_statistics.average_away_goals
            )

        # --------------------------------------------------
        # Historiska matcher för aktuella lag
        # --------------------------------------------------

        home_model_matches = (
            data.team_model_matches.get(
                data.home_team.id,
                []
            )
        )

        away_model_matches = (
            data.team_model_matches.get(
                data.away_team.id,
                []
            )
        )

        # --------------------------------------------------
        # Attack och försvar
        # --------------------------------------------------

        self._calculate_weighted_team_coefficients(
            data.home_statistics,
            home_model_matches,
            average_home_goals,
            average_away_goals,
            data.reference_date,
            data.season.competition
        )

        self._calculate_weighted_team_coefficients(
            data.away_statistics,
            away_model_matches,
            average_home_goals,
            average_away_goals,
            data.reference_date,
            data.season.competition
        )

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        self._calculate_recent_form(
            data.home_statistics,
            home_model_matches
        )

        self._calculate_recent_form(
            data.away_statistics,
            away_model_matches
        )

        # --------------------------------------------------
        # Förväntat antal mål
        # --------------------------------------------------

        lambda_home = self._calculate_lambda_home(
            average_home_goals,
            data.home_statistics,
            data.away_statistics
        )

        lambda_away = self._calculate_lambda_away(
            average_away_goals,
            data.home_statistics,
            data.away_statistics
        )

        # --------------------------------------------------
        # Marginala Poissonfördelningar
        # --------------------------------------------------

        home_poisson = (
            self._calculate_poisson_distribution(
                lambda_home
            )
        )

        away_poisson = (
            self._calculate_poisson_distribution(
                lambda_away
            )
        )

        # --------------------------------------------------
        # Dixon-Coles rho
        # --------------------------------------------------

        rho = self._estimate_rho(
            data
        )

        # --------------------------------------------------
        # Resultatmatris
        # --------------------------------------------------

        score_matrix = self._calculate_score_matrix(
            lambda_home,
            lambda_away,
            rho
        )

        # --------------------------------------------------
        # Mest sannolika resultat
        # --------------------------------------------------

        most_likely_scores = (
            self._get_most_likely_scores(
                score_matrix
            )
        )

        # --------------------------------------------------
        # 1X2
        # --------------------------------------------------

        (
            probability_1,
            probability_x,
            probability_2
        ) = self._calculate_match_probabilities(
            score_matrix
        )

        # --------------------------------------------------
        # Över / under 2,5
        # --------------------------------------------------

        (
            probability_over_25,
            probability_under_25
        ) = self._calculate_over_under_probabilities(
            score_matrix
        )

        # --------------------------------------------------
        # BTTS
        # --------------------------------------------------

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
            Beräknar lagets form utifrån
            de senaste matcherna.
        """
        completed_matches = [
            match
            for match in matches
            if (
                match.home_score is not None
                and match.away_score is not None
            )
        ]

        completed_matches.sort(
            key=lambda match: match.match_date,
            reverse=True
        )

        recent_matches = completed_matches[
            :self.FORM_MATCHES
        ]

        form_points = 0
        played_matches = 0

        for match in recent_matches:
            if (
                match.home_team.id
                == statistics.team.id
            ):
                goals_for = match.home_score
                goals_against = match.away_score

            elif (
                match.away_team.id
                == statistics.team.id
            ):
                goals_for = match.away_score
                goals_against = match.home_score

            else:
                continue

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
    # Lambda
    # --------------------------------------------------

    def _clamp_lambda(
        self,
        lambda_value
    ):
        """
            Begränsar lambda till tillåtet intervall.
        """
        return min(
            max(
                lambda_value,
                self.MIN_LAMBDA_VALUE
            ),
            self.MAX_LAMBDA_VALUE
        )

    def _calculate_lambda_home(
        self,
        average_home_goals,
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
            average_home_goals
            * home_statistics.home_attack_coefficient
            * away_statistics.away_defence_coefficient
            * form_factor
        )

        return self._clamp_lambda(
            lambda_home
        )

    def _calculate_lambda_away(
        self,
        average_away_goals,
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
            average_away_goals
            * away_statistics.away_attack_coefficient
            * home_statistics.home_defence_coefficient
            * form_factor
        )

        return self._clamp_lambda(
            lambda_away
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
            max(
                probability_max_plus,
                self.MIN_PROBABILITY
            )
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

                tau = (
                    self._calculate_dixon_coles_tau(
                        home_goals,
                        away_goals,
                        lambda_home,
                        lambda_away,
                        rho
                    )
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

        return scores[
            :count
        ]

    # --------------------------------------------------
    # Rho
    # --------------------------------------------------

    def _calculate_rho_log_likelihood(
        self,
        data,
        rho
    ):
        """
            Beräknar tidsviktad log-likelihood
            för ett givet Dixon-Coles-rho.

            Varje historisk match bedöms endast
            utifrån information som fanns före
            matchens datum.
        """
        log_likelihood = 0.0

        for match in data.league_model_matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            # Hämta endast ligamatcher som spelades
            # före den historiska matchen.
            historical_matches = (
                self._get_matches_before_date(
                    data.league_model_matches,
                    match.match_date
                )
            )

            if not historical_matches:
                continue

            # Ligans nivå så som den såg ut
            # vid den historiska matchen.
            (
                average_home_goals,
                average_away_goals
            ) = self._calculate_weighted_league_averages(
                historical_matches,
                match.match_date
            )

            if (
                average_home_goals is None
                or average_away_goals is None
            ):
                continue

            # Hemmalagets historik före matchen.
            home_matches = self._get_team_matches(
                historical_matches,
                match.home_team.id
            )

            # Bortalagets historik före matchen.
            away_matches = self._get_team_matches(
                historical_matches,
                match.away_team.id
            )

            # Lagstyrkor vid tidpunkten för matchen.
            (
                home_home_attack,
                home_away_attack,
                home_home_defence,
                home_away_defence
            ) = self._get_weighted_team_coefficients(
                home_matches,
                match.home_team.id,
                average_home_goals,
                average_away_goals,
                match.match_date,
                data.season.competition
            )

            (
                away_home_attack,
                away_away_attack,
                away_home_defence,
                away_away_defence
            ) = self._get_weighted_team_coefficients(
                away_matches,
                match.away_team.id,
                average_home_goals,
                average_away_goals,
                match.match_date,
                data.season.competition
            )

            # Hemmalagets lambda vid den
            # historiska matchens tidpunkt.
            lambda_home = (
                average_home_goals
                * home_home_attack
                * away_away_defence
            )

            lambda_home = self._clamp_lambda(
                lambda_home
            )

            # Bortalagets lambda vid den
            # historiska matchens tidpunkt.
            lambda_away = (
                average_away_goals
                * away_away_attack
                * home_home_defence
            )

            lambda_away = self._clamp_lambda(
                lambda_away
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

            # Nyare historiska matcher får
            # större betydelse för dagens rho.
            weight = (
                self._calculate_time_weight(
                    match.match_date,
                    data.reference_date
                )
            )

            log_likelihood += (
                weight
                * math.log(tau)
            )

        return log_likelihood

    def _estimate_rho(
        self,
        data
    ):
        """
            Skattar Dixon-Coles rho genom att
            maximera tidsviktad log-likelihood.
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

    # --------------------------------------------------
    # Viktning
    # --------------------------------------------------

    def _calculate_time_weight(
        self,
        match_date,
        reference_date
    ):
        """
            Beräknar tidsvikten för en match.
        """
        days_old = (
            reference_date
            - match_date
        ).days

        if days_old < 0:
            return 0.0

        return math.exp(
            -self.TIME_DECAY
            * days_old
        )

    def _calculate_competition_weight(
        self,
        match,
        target_competition
    ):
        """
            Beräknar vikten för matchens tävling
            i förhållande till måltävlingen.
        """
        match_competition = (
            match.season.competition
        )

        if (
            match_competition.id
            == target_competition.id
        ):
            return 1.0

        return self.OTHER_COMPETITION_WEIGHT

    # --------------------------------------------------
    # Historiska matcher
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

    def _get_matches_before_date(
        self,
        matches,
        before_date
    ):
        """
            Returnerar matcher som spelades
            före angivet datum.
        """
        return [
            match
            for match in matches
            if match.match_date < before_date
        ]

    # --------------------------------------------------
    # Historiskt viktade laggenomsnitt
    # --------------------------------------------------

    def _calculate_weighted_team_averages(
        self,
        matches,
        team_id,
        reference_date,
        target_competition
    ):
        """
            Beräknar viktade målgenomsnitt
            hemma och borta för ett lag.
        """
        home_weight = 0.0
        away_weight = 0.0

        home_goals_for = 0.0
        home_goals_against = 0.0

        away_goals_for = 0.0
        away_goals_against = 0.0

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            time_weight = (
                self._calculate_time_weight(
                    match.match_date,
                    reference_date
                )
            )

            competition_weight = (
                self._calculate_competition_weight(
                    match,
                    target_competition
                )
            )

            weight = (
                time_weight
                * competition_weight
            )

            if weight <= 0:
                continue

            if (
                match.home_team.id
                == team_id
            ):
                home_goals_for += (
                    match.home_score
                    * weight
                )

                home_goals_against += (
                    match.away_score
                    * weight
                )

                home_weight += weight

            elif (
                match.away_team.id
                == team_id
            ):
                away_goals_for += (
                    match.away_score
                    * weight
                )

                away_goals_against += (
                    match.home_score
                    * weight
                )

                away_weight += weight

        return {
            "home_goals_for": (
                home_goals_for
                / home_weight
                if home_weight > 0
                else None
            ),
            "home_goals_against": (
                home_goals_against
                / home_weight
                if home_weight > 0
                else None
            ),
            "away_goals_for": (
                away_goals_for
                / away_weight
                if away_weight > 0
                else None
            ),
            "away_goals_against": (
                away_goals_against
                / away_weight
                if away_weight > 0
                else None
            )
        }

    # --------------------------------------------------
    # Historiskt viktade ligagenomsnitt
    # --------------------------------------------------

    def _calculate_weighted_league_averages(
        self,
        matches,
        reference_date
    ):
        """
            Beräknar tidsviktade genomsnitt
            för hemma- och bortamål i ligan.
        """
        home_goals = 0.0
        away_goals = 0.0
        total_weight = 0.0

        for match in matches:
            if (
                match.home_score is None
                or match.away_score is None
            ):
                continue

            weight = (
                self._calculate_time_weight(
                    match.match_date,
                    reference_date
                )
            )

            if weight <= 0:
                continue

            home_goals += (
                match.home_score
                * weight
            )

            away_goals += (
                match.away_score
                * weight
            )

            total_weight += weight

        if total_weight == 0:
            return (
                None,
                None
            )

        return (
            home_goals / total_weight,
            away_goals / total_weight
        )

    # --------------------------------------------------
    # Historiskt viktade lagkoefficienter
    # --------------------------------------------------

    def _get_weighted_team_coefficients(
        self,
        matches,
        team_id,
        average_home_goals,
        average_away_goals,
        reference_date,
        target_competition
    ):
        """
            Returnerar historiskt viktade
            attack- och försvarskoefficienter
            utan att ändra TeamStatistics.
        """
        averages = (
            self._calculate_weighted_team_averages(
                matches,
                team_id,
                reference_date,
                target_competition
            )
        )

        home_goals_for = (
            averages["home_goals_for"]
        )

        home_goals_against = (
            averages["home_goals_against"]
        )

        away_goals_for = (
            averages["away_goals_for"]
        )

        away_goals_against = (
            averages["away_goals_against"]
        )

        home_attack = (
            home_goals_for
            / average_home_goals
            if (
                home_goals_for is not None
                and average_home_goals > 0
            )
            else self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
        )

        away_attack = (
            away_goals_for
            / average_away_goals
            if (
                away_goals_for is not None
                and average_away_goals > 0
            )
            else self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
        )

        home_defence = (
            home_goals_against
            / average_away_goals
            if (
                home_goals_against is not None
                and average_away_goals > 0
            )
            else self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
        )

        away_defence = (
            away_goals_against
            / average_home_goals
            if (
                away_goals_against is not None
                and average_home_goals > 0
            )
            else self.DEFAULT_ATTACK_DEFENCE_COEFFICIENTS
        )

        return (
            home_attack,
            away_attack,
            home_defence,
            away_defence
        )

    def _calculate_weighted_team_coefficients(
        self,
        statistics,
        matches,
        average_home_goals,
        average_away_goals,
        reference_date,
        target_competition
    ):
        """
            Beräknar och sparar historiskt viktade
            attack- och försvarskoefficienter.
        """
        (
            home_attack,
            away_attack,
            home_defence,
            away_defence
        ) = self._get_weighted_team_coefficients(
            matches,
            statistics.team.id,
            average_home_goals,
            average_away_goals,
            reference_date,
            target_competition
        )

        statistics.home_attack_coefficient = (
            home_attack
        )

        statistics.away_attack_coefficient = (
            away_attack
        )

        statistics.home_defence_coefficient = (
            home_defence
        )

        statistics.away_defence_coefficient = (
            away_defence
        )
