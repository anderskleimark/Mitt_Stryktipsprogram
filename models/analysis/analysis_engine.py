import math

from models.analysis.dixon_coles_model import DixonColesModel
from models.domains import BetAnalysis, MatchAnalysis, OddsAnalysis


class AnalysisEngine:
    """
        Genomför matchanalys med en gemensamt skattad Dixon-Coles-modell.
    """

    MAX_POISSON_GOALS = 5
    MAX_SCORE_MATRIX_GOALS = 10

    OVER_UNDER_LINES = (
        1.5,
        2.5,
        3.5,
        4.5
    )

    MIN_LAMBDA_VALUE = 0.1
    MAX_LAMBDA_VALUE = 5.0

    FORM_MATCHES = 5

    WIN_SCORE = 3
    DRAW_SCORE = 1

    DEFAULT_RECENT_FORM = 0.5
    NUMBER_OF_RESULTS = 5
    VALUE_MARGIN = 0.05

    def __init__(self):
        self.dixon_coles_model = DixonColesModel()

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
        competition_id = data.season.competition.id

        parameters = (
            self.dixon_coles_model.fit(
                data.model_matches,
                data.reference_date,
                competition_id
            )
        )

        lambda_home, lambda_away = (
            self.dixon_coles_model.calculate_expected_goals(
                parameters,
                data.home_team.id,
                data.away_team.id,
                competition_id
            )
        )

        lambda_home = self._clamp_lambda(lambda_home)
        lambda_away = self._clamp_lambda(lambda_away)

        # Parametrar till befintlig vy.
        self._update_team_model_statistics(
            data.home_statistics,
            parameters.attack[data.home_team.id],
            parameters.defence[data.home_team.id]
        )

        self._update_team_model_statistics(
            data.away_statistics,
            parameters.attack[data.away_team.id],
            parameters.defence[data.away_team.id]
        )

        # Form för visning.
        self._calculate_recent_form(
            data.home_statistics,
            data.team_model_matches.get(data.home_team.id, [])
        )

        self._calculate_recent_form(
            data.away_statistics,
            data.team_model_matches.get(data.away_team.id, [])
        )

        home_poisson = self._calculate_poisson_distribution(lambda_home)
        away_poisson = self._calculate_poisson_distribution(lambda_away)

        score_matrix = self._calculate_score_matrix(
            lambda_home,
            lambda_away,
            parameters.rho
        )

        (
            probability_1,
            probability_x,
            probability_2
        ) = self._calculate_match_probabilities(score_matrix)

        double_chance_probabilities = (
            self._calculate_double_chance_probabilities(
                probability_1,
                probability_x,
                probability_2
            )
        )

        over_under_probabilities = {}
        for line in self.OVER_UNDER_LINES:
            (
                probability_over,
                probability_under
            ) = self._calculate_over_under_probabilities(
                score_matrix,
                line
            )

            over_under_probabilities[line] = {
                "over": probability_over,
                "under": probability_under
            }

        probability_btts = self._calculate_btts_probabilities(score_matrix)

        odds_analysis = self._create_odds_analysis(
            probability_1,
            probability_x,
            probability_2,
            double_chance_probabilities,
            over_under_probabilities,
            probability_btts
        )

        most_likely_scores = self._get_most_likely_scores(score_matrix)

        return MatchAnalysis(
            home_statistics=data.home_statistics,
            away_statistics=data.away_statistics,
            h2h_statistics=data.h2h_statistics,

            lambda_home=lambda_home,
            lambda_away=lambda_away,

            home_poisson=home_poisson,
            away_poisson=away_poisson,

            rho=parameters.rho,

            most_likely_scores=most_likely_scores,
            score_matrix=score_matrix,
            odds_analysis=odds_analysis
        )

    # --------------------------------------------------
    # Modellparametrar för vyn
    # --------------------------------------------------

    def _update_team_model_statistics(
        self,
        statistics,
        attack,
        defence
    ):
        """
            Översätter modellens log-parametrar till befintliga visningskoefficienter.
        """
        attack_coefficient = math.exp(attack)
        defence_coefficient = math.exp(-defence)

        statistics.home_attack_coefficient = attack_coefficient
        statistics.away_attack_coefficient = attack_coefficient
        statistics.home_defence_coefficient = defence_coefficient
        statistics.away_defence_coefficient = defence_coefficient

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _calculate_recent_form(
        self,
        statistics,
        matches
    ):
        completed_matches = [
            match
            for match in matches
            if match.home_score is not None and match.away_score is not None
        ]

        completed_matches.sort(
            key=lambda match: match.match_date,
            reverse=True
        )

        recent_matches = completed_matches[:self.FORM_MATCHES]
        form_points = 0

        for match in recent_matches:
            if match.home_team.id == statistics.team.id:
                goals_for = match.home_score
                goals_against = match.away_score

            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for > goals_against:
                form_points += self.WIN_SCORE

            elif goals_for == goals_against:
                form_points += self.DRAW_SCORE

        if not recent_matches:
            statistics.recent_form = self.DEFAULT_RECENT_FORM
            return

        statistics.recent_form = (
            form_points / (len(recent_matches) * self.WIN_SCORE)
        )

    # --------------------------------------------------
    # Lambda
    # --------------------------------------------------

    def _clamp_lambda(
        self,
        lambda_value
    ):
        return min(
            max(lambda_value, self.MIN_LAMBDA_VALUE), self.MAX_LAMBDA_VALUE)

    # --------------------------------------------------
    # Poisson
    # --------------------------------------------------

    def _calculate_poisson_probability(
        self,
        goals,
        lambda_value
    ):
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
        if max_goals is None:
            max_goals = self.MAX_POISSON_GOALS

        probabilities = []

        for goals in range(max_goals):
            probabilities.append(
                self._calculate_poisson_probability(goals, lambda_value)
            )

        probabilities.append(max(0.0, 1.0 - sum(probabilities)))

        return probabilities

    # --------------------------------------------------
    # Dixon-Coles
    # --------------------------------------------------

    def _calculate_dixon_coles_tau(
        self,
        *,
        home_goals,
        away_goals,
        lambda_home,
        lambda_away,
        rho
    ):
        if home_goals == 0 and away_goals == 0:
            return 1 - lambda_home * lambda_away * rho

        if home_goals == 0 and away_goals == 1:
            return 1 + lambda_home * rho

        if home_goals == 1 and away_goals == 0:
            return 1 + lambda_away * rho

        if home_goals == 1 and away_goals == 1:
            return 1 - rho
        return 1.0

    def _calculate_score_matrix(
        self,
        lambda_home,
        lambda_away,
        rho
    ):
        """
            Beräknar och normaliserar sannolikhetsmatrisen
            för möjliga matchresultat.
        """
        matrix = []

        for home_goals in range(self.MAX_SCORE_MATRIX_GOALS + 1):
            row = []

            for away_goals in range(self.MAX_SCORE_MATRIX_GOALS + 1):
                probability = (
                    self._calculate_poisson_probability(
                        home_goals,
                        lambda_home
                    )
                    * self._calculate_poisson_probability(
                        away_goals,
                        lambda_away
                    )
                    * self._calculate_dixon_coles_tau(
                        home_goals=home_goals,
                        away_goals=away_goals,
                        lambda_home=lambda_home,
                        lambda_away=lambda_away,
                        rho=rho
                    )
                )

                row.append(probability)

            matrix.append(row)

        total_probability = sum(
            probability
            for row in matrix
            for probability in row
        )

        if total_probability <= 0:
            raise ValueError(
                "Resultatmatrisens totala sannolikhet är ogiltig."
            )

        return [
            [
                probability / total_probability
                for probability in row
            ]
            for row in matrix
        ]

    # --------------------------------------------------
    # 1X2
    # --------------------------------------------------

    def _calculate_match_probabilities(
        self,
        score_matrix
    ):
        probability_1 = 0.0
        probability_x = 0.0
        probability_2 = 0.0

        for home_goals, row in enumerate(score_matrix):
            for away_goals, probability in enumerate(row):
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
    # Dubbelchans
    # --------------------------------------------------

    def _calculate_double_chance_probabilities(
        self,
        probability_1,
        probability_x,
        probability_2
    ):
        """
            Beräknar sannolikheterna för dubbelchans.
        """
        return {
            "1X": probability_1 + probability_x,
            "12": probability_1 + probability_2,
            "X2": probability_x + probability_2
        }

    # --------------------------------------------------
    # Över / under
    # --------------------------------------------------

    def _calculate_over_under_probabilities(
        self,
        score_matrix,
        line
    ):
        """
            Beräknar sannolikheten för över och under
            en angiven mållina.
        """
        probability_over = 0.0
        probability_under = 0.0

        for home_goals, row in enumerate(score_matrix):
            for away_goals, probability in enumerate(row):
                total_goals = home_goals + away_goals

                if total_goals > line:
                    probability_over += probability

                else:
                    probability_under += probability

        return (
            probability_over,
            probability_under
        )

    # --------------------------------------------------
    # BTTS
    # --------------------------------------------------

    def _calculate_btts_probabilities(
        self,
        score_matrix
    ):
        """
            Beräknar sannolikheterna för
            båda lagen gör mål, ja och nej.
        """
        probability_yes = 0.0

        for home_goals, row in enumerate(score_matrix):
            for away_goals, probability in enumerate(row):
                if home_goals > 0 and away_goals > 0:
                    probability_yes += probability

        probability_no = 1.0 - probability_yes

        return {
            "yes": probability_yes,
            "no": probability_no
        }

    # --------------------------------------------------
    # Mest sannolika result
    # --------------------------------------------------

    def _get_most_likely_scores(
        self,
        score_matrix,
        count=None
    ):
        if count is None:
            count = self.NUMBER_OF_RESULTS

        scores = []

        for home_goals, row in enumerate(score_matrix):
            for away_goals, probability in enumerate(row):
                scores.append(
                    (
                        home_goals,
                        away_goals,
                        probability
                    )
                )
        scores.sort(key=lambda score: score[2], reverse=True)
        return scores[:count]

    # --------------------------------------------------
    # Odds
    # --------------------------------------------------

    def _calculate_fair_odds(
        self,
        probability
    ):
        """
            Beräknar rättvist odds utifrån
            modellens sannolikhet.
        """
        if probability <= 0:
            return math.inf

        return 1.0 / probability

    def _calculate_odds_value(
        self,
        probability,
        odds
    ):
        """
            Beräknar spelvärdet för ett odds.

            1.00 innebär neutralt värde.
            Över 1.00 innebär överodds.
            Under 1.00 innebär underodds.
        """
        return probability * odds

    def _calculate_value_percentage(
        self,
        probability,
        odds
    ):
        """
            Beräknar spelvärdet uttryckt i procent.
        """
        return (
            probability * odds - 1.0
        ) * 100.0

    def _calculate_fair_odds(
        self,
        probability
    ):
        """
            Beräknar rättvist odds utifrån
            modellens sannolikhet.
        """
        if probability <= 0:
            return math.inf

        return 1.0 / probability

    def _create_bet_analysis(
        self,
        probability
    ):
        """
            Skapar analys för ett spelalternativ.
        """
        fair_odds = self._calculate_fair_odds(
            probability
        )

        return BetAnalysis(
            probability=probability,
            fair_odds=fair_odds,
            minimum_odds=self._calculate_minimum_odds(
                fair_odds
            )
        )

    def _create_odds_analysis(
        self,
        probability_1,
        probability_x,
        probability_2,
        double_chance_probabilities,
        over_under_probabilities,
        btts_probabilities
    ):
        """
            Skapar oddsanalysen för samtliga
            spelmarknader.
        """
        match_result = {
            "1": self._create_bet_analysis(
                probability_1
            ),
            "X": self._create_bet_analysis(
                probability_x
            ),
            "2": self._create_bet_analysis(
                probability_2
            )
        }

        double_chance = {
            result: self._create_bet_analysis(
                probability
            )
            for result, probability
            in double_chance_probabilities.items()
        }

        over_under = {}

        for line, probabilities in over_under_probabilities.items():
            over_under[line] = {
                "over": self._create_bet_analysis(
                    probabilities["over"]
                ),
                "under": self._create_bet_analysis(
                    probabilities["under"]
                )
            }

        btts = {
            result: self._create_bet_analysis(
                probability
            )
            for result, probability
            in btts_probabilities.items()
        }

        return OddsAnalysis(
            match_result=match_result,
            double_chance=double_chance,
            over_under=over_under,
            btts=btts
        )

    def _calculate_minimum_odds(
        self,
        fair_odds
    ):
        """
            Beräknar lägsta odds som betraktas
            som spelvärt efter säkerhetsmarginal.
        """
        return fair_odds * (1.0 + self.VALUE_MARGIN)
