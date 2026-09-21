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

    NUMBER_OF_RESULTS = 8
    VALUE_MARGIN = 0.05

    def __init__(self):
        self.dixon_coles_model = DixonColesModel()

    # --------------------------------------------------
    # Analys
    # --------------------------------------------------

    def fit_model(
        self,
        model_matches,
        reference_date,
        competition_id,
        *,
        time_decay=None,
        history_years=None,
        training_scope=None,
        rho_mode=None,
        home_advantage_mode=None
    ):
        """
            Anpassar modellparametrarna med valda modellinställningar.
        """
        return self.dixon_coles_model.fit(
            model_matches,
            reference_date,
            competition_id,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=rho_mode,
            home_advantage_mode=home_advantage_mode
        )

    def analyze_match(
        self,
        data,
        *,
        time_decay=None,
        form_weight=None,
        calculate_form=True,
        home_form_matches=None,
        away_form_matches=None,
        form_expectations=None,
        h2h_weight=None,
        calculate_h2h=True,
        h2h_matches=None,
        h2h_expectations=None,
        parameters=None
    ):
        """
            Analyserar en fotbollsmatch.
        """
        competition_id = data.season.competition.id

        if parameters is None:
            parameters = self.fit_model(
                data.model_matches,
                data.reference_date,
                competition_id,
                time_decay=time_decay
            )

        lambda_home, lambda_away = self.dixon_coles_model.calculate_expected_goals(
            parameters,
            data.home_team.id,
            data.away_team.id,
            competition_id
        )

        if calculate_form:
            home_attack_residual, home_defence_residual = self._calculate_form_goal_residuals(
                team_id=data.home_team.id,
                matches=home_form_matches,
                expectations=form_expectations
            )

            away_attack_residual, away_defence_residual = self._calculate_form_goal_residuals(
                team_id=data.away_team.id,
                matches=away_form_matches,
                expectations=form_expectations
            )

            home_attack_residual = max(-1.0, min(1.0, home_attack_residual))
            home_defence_residual = max(-1.0, min(1.0, home_defence_residual))
            away_attack_residual = max(-1.0, min(1.0, away_attack_residual))
            away_defence_residual = max(-1.0, min(1.0, away_defence_residual))

            home_form = self._calculate_form_value(
                home_attack_residual,
                home_defence_residual
            )

            away_form = self._calculate_form_value(
                away_attack_residual,
                away_defence_residual
            )

            data.home_statistics.recent_form = home_form
            data.away_statistics.recent_form = away_form

            lambda_home, lambda_away = self._apply_form_adjustment(
                lambda_home=lambda_home,
                lambda_away=lambda_away,
                home_attack_residual=home_attack_residual,
                home_defence_residual=home_defence_residual,
                away_attack_residual=away_attack_residual,
                away_defence_residual=away_defence_residual,
                form_weight=form_weight
            )

        else:
            data.home_statistics.recent_form = 0.5
            data.away_statistics.recent_form = 0.5

        if calculate_h2h and h2h_weight != 0.0:
            h2h_difference = self._calculate_h2h_difference(
                home_team_id=data.home_team.id,
                matches=h2h_matches,
                expectations=h2h_expectations
            )

            lambda_home, lambda_away = self._apply_h2h_adjustment(
                lambda_home=lambda_home,
                lambda_away=lambda_away,
                h2h_difference=h2h_difference,
                h2h_weight=h2h_weight
            )

        lambda_home = self._clamp_lambda(lambda_home)
        lambda_away = self._clamp_lambda(lambda_away)

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

        home_poisson = self._calculate_poisson_distribution(lambda_home)
        away_poisson = self._calculate_poisson_distribution(lambda_away)

        score_matrix = self._calculate_score_matrix(
            lambda_home,
            lambda_away,
            parameters.rho
        )

        probability_1, probability_x, probability_2 = (
            self._calculate_match_probabilities(score_matrix)
        )

        double_chance_probabilities = self._calculate_double_chance_probabilities(
            probability_1,
            probability_x,
            probability_2
        )

        over_under_probabilities = {}

        for line in self.OVER_UNDER_LINES:
            probability_over, probability_under = (
                self._calculate_over_under_probabilities(
                    score_matrix,
                    line
                )
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
            home_advantage=parameters.home_advantage,
            most_likely_scores=most_likely_scores,
            score_matrix=score_matrix,
            odds_analysis=odds_analysis,
            home_form_matches=home_form_matches or [],
            away_form_matches=away_form_matches or []
        )

    def _calculate_h2h_goal_residual(
        self,
        *,
        team_id,
        matches,
        expectations
    ):
        """
            Beräknar genomsnittlig målresidual för ett lag
            i historiska H2H-matcher.
        """
        if not matches:
            return 0.0

        residual_sum = 0.0

        for match in matches:
            expectation = expectations[match.id]

            if match.home_team.id == team_id:
                goals = match.home_score
                expected_goals = expectation.home_expected_goals
            else:
                goals = match.away_score
                expected_goals = expectation.away_expected_goals

            residual_sum += goals - expected_goals

        return residual_sum / len(matches)

    @staticmethod
    def _apply_h2h_adjustment(
        *,
        lambda_home,
        lambda_away,
        home_h2h_residual,
        away_h2h_residual,
        h2h_weight
    ):
        """
            Justerar förväntade mål utifrån historiska H2H-målresidualer.
        """
        lambda_home *= math.exp(h2h_weight * home_h2h_residual)
        lambda_away *= math.exp(h2h_weight * away_h2h_residual)

        return lambda_home, lambda_away

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
            Uppdaterar lagets modellbaserade statistik.
        """
        statistics.playing_style = self._calculate_playing_style(
            attack,
            defence
        )
        print(
            f"{statistics.team.team_name}: "
            f"attack={attack:.4f}, "
            f"defence={defence:.4f}, "
            f"style={statistics.playing_style:.4f}"
        )

    @staticmethod
    def _calculate_playing_style(attack, defence):
        """
            Beräknar lagets spelstil på skalan 0–1.

            0.0 = defensiv
            0.5 = balanserad
            1.0 = offensiv
        """
        style_difference = attack + defence

        return 1.0 / (1.0 + math.exp(-style_difference))

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    @staticmethod
    def _calculate_form_value(attack_residual, defence_residual):
        """
            Omvandlar offensiv och defensiv målresidual
            till ett formvärde mellan 0 och 1.

            0.5 motsvarar neutral form.
        """
        form_residual = (attack_residual - defence_residual) / 2.0

        return 1.0 / (1.0 + math.exp(-form_residual))

    @staticmethod
    def _calculate_result_form(team_id, matches):
        """
            Beräknar traditionell resultatform mellan 0 och 1.

            Vinst = 1.0
            Oavgjort = 0.5
            Förlust = 0.0
        """
        if not matches:
            return 0.5

        total = 0.0

        for match in matches:
            if match.home_team.id == team_id:
                goals_for = match.home_score
                goals_against = match.away_score
            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for > goals_against:
                total += 1.0
            elif goals_for == goals_against:
                total += 0.5

        return total / len(matches)

    def _calculate_form_goal_residuals(
        self,
        *,
        team_id,
        matches,
        expectations
    ):
        """
            Beräknar genomsnittliga offensiva och defensiva
            målresidualer för ett lag i de senaste matcherna.
        """
        if not matches:
            return 0.0, 0.0

        attack_residual_sum = 0.0
        defence_residual_sum = 0.0

        for match in matches:
            expectation = expectations[match.id]

            if match.home_team.id == team_id:
                opponent = match.away_team
                goals_for = match.home_score
                goals_against = match.away_score
                expected_goals_for = expectation.home_expected_goals
                expected_goals_against = expectation.away_expected_goals
            else:
                opponent = match.home_team
                goals_for = match.away_score
                goals_against = match.home_score
                expected_goals_for = expectation.away_expected_goals
                expected_goals_against = expectation.home_expected_goals

            attack_residual = goals_for - expected_goals_for
            defence_residual = goals_against - expected_goals_against

            attack_residual_sum += attack_residual
            defence_residual_sum += defence_residual

        match_count = len(matches)

        attack_residual = attack_residual_sum / match_count
        defence_residual = defence_residual_sum / match_count

        return attack_residual, defence_residual

    @staticmethod
    def _apply_form_adjustment(
        *,
        lambda_home,
        lambda_away,
        home_attack_residual,
        home_defence_residual,
        away_attack_residual,
        away_defence_residual,
        form_weight
    ):
        """
                Justerar förväntade mål utifrån offensiva
                och defensiva målresidualer.
            """
        home_form_residual = (
            home_attack_residual + away_defence_residual
        ) / 2.0

        away_form_residual = (
            away_attack_residual + home_defence_residual
        ) / 2.0

        lambda_home *= math.exp(form_weight * home_form_residual)
        lambda_away *= math.exp(form_weight * away_form_residual)

        return lambda_home, lambda_away

    # --------------------------------------------------
    # Lambda
    # --------------------------------------------------

    def _clamp_lambda(
        self,
        lambda_value
    ):
        return min(
            max(lambda_value, self.MIN_LAMBDA_VALUE),
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
                self._calculate_poisson_probability(
                    goals,
                    lambda_value
                )
            )

        probabilities.append(
            max(
                0.0,
                1.0 - sum(probabilities)
            )
        )

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
        home_probabilities = [
            self._calculate_poisson_probability(
                goals,
                lambda_home
            )
            for goals in range(
                self.MAX_SCORE_MATRIX_GOALS + 1
            )
        ]

        away_probabilities = [
            self._calculate_poisson_probability(
                goals,
                lambda_away
            )
            for goals in range(
                self.MAX_SCORE_MATRIX_GOALS + 1
            )
        ]

        matrix = []

        for home_goals, home_probability in enumerate(
            home_probabilities
        ):
            row = []

            for away_goals, away_probability in enumerate(
                away_probabilities
            ):
                probability = (
                    home_probability
                    * away_probability
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

        inverse_total_probability = (
            1.0 / total_probability
        )

        return [
            [
                probability * inverse_total_probability
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
    # Mest sannolika resultat
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

        scores.sort(
            key=lambda score: score[2],
            reverse=True
        )

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
