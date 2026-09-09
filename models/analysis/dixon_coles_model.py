import math

import numpy as np
from scipy.optimize import minimize

from models.domains import DixonColesParameters


class DixonColesModel:
    """
    Gemensam Dixon-Coles-modell för flera tävlingar.

    Attack, försvar, hemmafördel och tävlingseffekter
    skattas samtidigt. Rho kan antingen vara fixerad
    till 0.0 eller skattas tillsammans med övriga parametrar.
    """

    # --------------------------------------------------
    # Tidsvikt
    # --------------------------------------------------

    TIME_DECAY = 0.0027

    # --------------------------------------------------
    # Rho-läge
    # --------------------------------------------------

    RHO_MODE_FIXED = "fixed"
    RHO_MODE_ESTIMATED = "estimated"

    DEFAULT_RHO_MODE = RHO_MODE_FIXED
    FIXED_RHO = 0.0

    # --------------------------------------------------
    # Parametergränser
    # --------------------------------------------------

    ATTACK_MIN = -2.5
    ATTACK_MAX = 2.5

    DEFENCE_MIN = -2.5
    DEFENCE_MAX = 2.5

    BASE_LOG_RATE_MIN = -1.5
    BASE_LOG_RATE_MAX = 1.5

    HOME_ADVANTAGE_MIN = -1.0
    HOME_ADVANTAGE_MAX = 1.0

    COMPETITION_EFFECT_MIN = -1.5
    COMPETITION_EFFECT_MAX = 1.5

    RHO_MIN = -0.30
    RHO_MAX = 0.30

    # --------------------------------------------------
    # Initialvärden
    # --------------------------------------------------

    INITIAL_RHO = -0.05

    # --------------------------------------------------
    # Optimering
    # --------------------------------------------------

    MAX_ITERATIONS = 3000
    OPTIMIZATION_TOLERANCE = 1e-8

    LARGE_PENALTY = 1e12

    # --------------------------------------------------
    # Mål
    # --------------------------------------------------

    MIN_AVERAGE_GOALS = 0.1

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self):
        self._last_parameters = None
        self._last_team_ids = None
        self._last_free_competition_ids = None
        self._last_reference_competition_id = None
        self._last_reference_date = None
        self._last_time_decay = None
        self._last_rho_mode = None

    # --------------------------------------------------
    # Publikt gränssnitt
    # --------------------------------------------------

    def fit(
        self,
        matches,
        reference_date,
        reference_competition_id,
        *,
        time_decay=None,
        rho_mode=None
    ):
        """
        Anpassar Dixon-Coles-modellen gemensamt
        till samtliga matcher.
        """
        if time_decay is None:
            time_decay = self.TIME_DECAY

        if rho_mode is None:
            rho_mode = self.DEFAULT_RHO_MODE

        self._validate_rho_mode(rho_mode)

        completed_matches = self._get_completed_matches(
            matches,
            reference_date
        )

        if not completed_matches:
            raise ValueError(
                "Det finns inga färdigspelade matcher "
                "för Dixon-Coles-modellen."
            )

        team_ids = self._get_team_ids(
            completed_matches
        )

        competition_ids = self._get_competition_ids(
            completed_matches
        )

        if len(team_ids) < 2:
            raise ValueError(
                "För få lag för Dixon-Coles-modellen."
            )

        if reference_competition_id not in competition_ids:
            raise ValueError(
                "Referenstävlingen saknas i modellens matcher."
            )

        free_competition_ids = [
            competition_id
            for competition_id in competition_ids
            if competition_id != reference_competition_id
        ]

        match_data = self._prepare_match_data(
            completed_matches,
            team_ids,
            free_competition_ids,
            reference_competition_id,
            reference_date,
            time_decay
        )

        standard_initial_parameters = self._create_initial_parameters(
            completed_matches,
            len(team_ids),
            len(free_competition_ids),
            rho_mode
        )

        initial_parameters = self._create_warm_start_parameters(
            standard_initial_parameters,
            team_ids,
            free_competition_ids,
            reference_competition_id,
            reference_date,
            time_decay,
            rho_mode
        )

        use_warm_start = (
            initial_parameters
            is not standard_initial_parameters
        )

        bounds = self._create_bounds(
            len(team_ids),
            len(free_competition_ids),
            rho_mode
        )

        constraints = self._create_constraints(
            len(team_ids)
        )

        result = minimize(
            self._negative_log_likelihood,
            initial_parameters,
            args=(
                match_data,
                len(team_ids),
                len(free_competition_ids),
                rho_mode
            ),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": self.MAX_ITERATIONS,
                "ftol": self.OPTIMIZATION_TOLERANCE,
                "disp": False
            }
        )

        print(
            "Dixon-Coles: "
            f"matcher={len(completed_matches)}, "
            f"lag={len(team_ids)}, "
            f"tävlingar={len(competition_ids)}, "
            f"iterationer={result.nit}, "
            f"funktionsanrop={result.nfev}, "
            f"time_decay={time_decay:.4f}, "
            f"rho_mode={rho_mode}, "
            f"warm_start={use_warm_start}, "
            f"success={result.success}"
        )

        if not result.success:
            raise RuntimeError(
                "Dixon-Coles-optimeringen misslyckades: "
                f"{result.message}"
            )

        self._store_warm_start(
            result.x,
            team_ids,
            free_competition_ids,
            reference_competition_id,
            reference_date,
            time_decay,
            rho_mode
        )

        (
            attack,
            defence,
            competition_effect,
            base_log_rate,
            home_advantage,
            rho
        ) = self._unpack_parameters(
            result.x,
            team_ids,
            free_competition_ids,
            reference_competition_id,
            rho_mode
        )

        return DixonColesParameters(
            attack=attack,
            defence=defence,
            competition_effect=competition_effect,
            base_log_rate=base_log_rate,
            home_advantage=home_advantage,
            rho=rho,
            reference_competition_id=reference_competition_id,
            success=True,
            negative_log_likelihood=float(result.fun),
            matches_used=len(completed_matches)
        )

    def _validate_rho_mode(self, rho_mode):
        """
        Kontrollerar att angivet rho-läge är giltigt.
        """
        if rho_mode not in (
            self.RHO_MODE_FIXED,
            self.RHO_MODE_ESTIMATED
        ):
            raise ValueError(
                f"Okänt rho-läge: {rho_mode}"
            )

    # --------------------------------------------------
    # Warm start
    # --------------------------------------------------

    def _create_warm_start_parameters(
        self,
        standard_parameters,
        team_ids,
        free_competition_ids,
        reference_competition_id,
        reference_date,
        time_decay,
        rho_mode
    ):
        """
        Skapar startparametrar från föregående
        lyckade optimering när det är lämpligt.

        Om warm start inte kan användas returneras
        de vanliga initialparametrarna.
        """
        if self._last_parameters is None:
            return standard_parameters

        if self._last_reference_competition_id != reference_competition_id:
            return standard_parameters

        if self._last_rho_mode != rho_mode:
            return standard_parameters

        if (
            self._last_time_decay is None
            or not math.isclose(
                self._last_time_decay,
                time_decay,
                rel_tol=0.0,
                abs_tol=1e-12
            )
        ):
            return standard_parameters

        if (
            self._last_reference_date is None
            or reference_date < self._last_reference_date
        ):
            return standard_parameters

        return self._map_previous_parameters(
            standard_parameters,
            team_ids,
            free_competition_ids,
            rho_mode
        )

    def _map_previous_parameters(
        self,
        standard_parameters,
        team_ids,
        free_competition_ids,
        rho_mode
    ):
        """
        Mappar parametrarna från föregående
        optimering till aktuell uppsättning
        lag och tävlingar.
        """
        parameters = np.asarray(
            standard_parameters,
            dtype=np.float64
        ).copy()

        old_team_ids = self._last_team_ids
        old_free_competition_ids = self._last_free_competition_ids
        old_parameters = self._last_parameters

        old_indexes = self._get_parameter_indexes(
            len(old_team_ids),
            len(old_free_competition_ids),
            rho_mode
        )

        new_indexes = self._get_parameter_indexes(
            len(team_ids),
            len(free_competition_ids),
            rho_mode
        )

        old_team_index = {
            team_id: index
            for index, team_id in enumerate(old_team_ids)
        }

        new_attack_values = parameters[
            new_indexes["attack_start"]:
            new_indexes["attack_end"]
        ]

        new_defence_values = parameters[
            new_indexes["defence_start"]:
            new_indexes["defence_end"]
        ]

        old_attack_values = old_parameters[
            old_indexes["attack_start"]:
            old_indexes["attack_end"]
        ]

        old_defence_values = old_parameters[
            old_indexes["defence_start"]:
            old_indexes["defence_end"]
        ]

        for new_index, team_id in enumerate(team_ids):
            old_index = old_team_index.get(team_id)

            if old_index is None:
                continue

            new_attack_values[new_index] = old_attack_values[old_index]
            new_defence_values[new_index] = old_defence_values[old_index]

        if len(new_attack_values) > 0:
            new_attack_values -= np.mean(new_attack_values)

        if len(new_defence_values) > 0:
            new_defence_values -= np.mean(new_defence_values)

        parameters[
            new_indexes["base_log_rate"]
        ] = old_parameters[
            old_indexes["base_log_rate"]
        ]

        parameters[
            new_indexes["home_advantage"]
        ] = old_parameters[
            old_indexes["home_advantage"]
        ]

        if rho_mode == self.RHO_MODE_ESTIMATED:
            parameters[
                new_indexes["rho"]
            ] = old_parameters[
                old_indexes["rho"]
            ]

        old_competition_index = {
            competition_id: index
            for index, competition_id
            in enumerate(old_free_competition_ids)
        }

        old_competition_values = old_parameters[
            old_indexes["competition_start"]:
            old_indexes["competition_end"]
        ]

        new_competition_values = parameters[
            new_indexes["competition_start"]:
            new_indexes["competition_end"]
        ]

        for new_index, competition_id in enumerate(free_competition_ids):
            old_index = old_competition_index.get(competition_id)

            if old_index is None:
                continue

            new_competition_values[new_index] = old_competition_values[old_index]

        return parameters

    def _store_warm_start(
        self,
        parameters,
        team_ids,
        free_competition_ids,
        reference_competition_id,
        reference_date,
        time_decay,
        rho_mode
    ):
        """
        Sparar resultatet från en lyckad
        optimering för nästa warm start.
        """
        self._last_parameters = np.asarray(
            parameters,
            dtype=np.float64
        ).copy()

        self._last_team_ids = list(team_ids)
        self._last_free_competition_ids = list(free_competition_ids)
        self._last_reference_competition_id = reference_competition_id
        self._last_reference_date = reference_date
        self._last_time_decay = float(time_decay)
        self._last_rho_mode = rho_mode

    def reset_warm_start(self):
        """
        Rensar tidigare sparade
        optimeringsparametrar.
        """
        self._last_parameters = None
        self._last_team_ids = None
        self._last_free_competition_ids = None
        self._last_reference_competition_id = None
        self._last_reference_date = None
        self._last_time_decay = None
        self._last_rho_mode = None

    # --------------------------------------------------
    # Prognos
    # --------------------------------------------------

    def calculate_expected_goals(
        self,
        parameters,
        home_team_id,
        away_team_id,
        competition_id
    ):
        """
        Beräknar förväntat antal mål
        från skattade parametrar.
        """
        if home_team_id not in parameters.attack:
            raise ValueError(
                "Hemmalaget saknas i "
                "Dixon-Coles-modellen."
            )

        if away_team_id not in parameters.attack:
            raise ValueError(
                "Bortalaget saknas i "
                "Dixon-Coles-modellen."
            )

        competition_effect = parameters.competition_effect.get(
            competition_id,
            0.0
        )

        lambda_home = math.exp(
            parameters.base_log_rate
            + parameters.home_advantage
            + competition_effect
            + parameters.attack[home_team_id]
            - parameters.defence[away_team_id]
        )

        lambda_away = math.exp(
            parameters.base_log_rate
            + competition_effect
            + parameters.attack[away_team_id]
            - parameters.defence[home_team_id]
        )

        return (
            lambda_home,
            lambda_away
        )

    # --------------------------------------------------
    # Matcher
    # --------------------------------------------------

    def _get_completed_matches(
        self,
        matches,
        reference_date
    ):
        """
        Returnerar färdigspelade matcher
        före referensdatumet.
        """
        return [
            match
            for match in matches
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date < reference_date
            )
        ]

    def _get_team_ids(self, matches):
        """
        Returnerar alla lag-id:n som
        finns i datamängden.
        """
        team_ids = set()

        for match in matches:
            team_ids.add(match.home_team.id)
            team_ids.add(match.away_team.id)

        return sorted(team_ids)

    def _get_competition_ids(self, matches):
        """
        Returnerar alla tävlings-id:n
        som finns i datamängden.
        """
        competition_ids = {
            match.season.competition.id
            for match in matches
        }

        return sorted(competition_ids)

    # --------------------------------------------------
    # Förbered matchdata
    # --------------------------------------------------

    def _prepare_match_data(
        self,
        matches,
        team_ids,
        free_competition_ids,
        reference_competition_id,
        reference_date,
        time_decay
    ):
        """
        Omvandlar historiska matcher till
        NumPy-arrayer som kan användas direkt
        i likelihood-funktionen.
        """
        team_index = {
            team_id: index
            for index, team_id in enumerate(team_ids)
        }

        competition_index = {
            competition_id: index
            for index, competition_id in enumerate(free_competition_ids)
        }

        home_team_indexes = []
        away_team_indexes = []
        competition_indexes = []
        home_goals = []
        away_goals = []
        weights = []
        home_log_factorials = []
        away_log_factorials = []

        for match in matches:
            home_team_indexes.append(
                team_index[match.home_team.id]
            )

            away_team_indexes.append(
                team_index[match.away_team.id]
            )

            competition_id = match.season.competition.id

            if competition_id == reference_competition_id:
                competition_indexes.append(-1)
            else:
                competition_indexes.append(
                    competition_index[competition_id]
                )

            home_goals.append(match.home_score)
            away_goals.append(match.away_score)

            days_old = (
                reference_date
                - match.match_date
            ).days

            weights.append(
                math.exp(
                    -time_decay
                    * days_old
                )
            )

            home_log_factorials.append(
                math.lgamma(match.home_score + 1)
            )

            away_log_factorials.append(
                math.lgamma(match.away_score + 1)
            )

        return {
            "home_team_indexes": np.asarray(
                home_team_indexes,
                dtype=np.int64
            ),
            "away_team_indexes": np.asarray(
                away_team_indexes,
                dtype=np.int64
            ),
            "competition_indexes": np.asarray(
                competition_indexes,
                dtype=np.int64
            ),
            "home_goals": np.asarray(
                home_goals,
                dtype=np.float64
            ),
            "away_goals": np.asarray(
                away_goals,
                dtype=np.float64
            ),
            "weights": np.asarray(
                weights,
                dtype=np.float64
            ),
            "home_log_factorials": np.asarray(
                home_log_factorials,
                dtype=np.float64
            ),
            "away_log_factorials": np.asarray(
                away_log_factorials,
                dtype=np.float64
            )
        }

    # --------------------------------------------------
    # Parameterindex
    # --------------------------------------------------

    def _get_parameter_indexes(
        self,
        number_of_teams,
        number_of_competitions,
        rho_mode
    ):
        """
        Returnerar indexgränser för
        parametervektorns olika delar.
        """
        attack_start = 0
        attack_end = number_of_teams

        defence_start = attack_end
        defence_end = defence_start + number_of_teams

        base_log_rate_index = defence_end
        home_advantage_index = base_log_rate_index + 1

        rho_index = None

        if rho_mode == self.RHO_MODE_ESTIMATED:
            rho_index = home_advantage_index + 1
            competition_start = rho_index + 1
        else:
            competition_start = home_advantage_index + 1

        competition_end = competition_start + number_of_competitions

        return {
            "attack_start": attack_start,
            "attack_end": attack_end,
            "defence_start": defence_start,
            "defence_end": defence_end,
            "base_log_rate": base_log_rate_index,
            "home_advantage": home_advantage_index,
            "rho": rho_index,
            "competition_start": competition_start,
            "competition_end": competition_end
        }

    # --------------------------------------------------
    # Initialvärden
    # --------------------------------------------------

    def _calculate_initial_goal_levels(self, matches):
        """
        Beräknar rimliga initialvärden
        för grundnivå och hemmafördel.
        """
        total_home_goals = 0
        total_away_goals = 0

        for match in matches:
            total_home_goals += match.home_score
            total_away_goals += match.away_score

        match_count = len(matches)

        average_home_goals = total_home_goals / match_count
        average_away_goals = total_away_goals / match_count

        average_away_goals = max(
            average_away_goals,
            self.MIN_AVERAGE_GOALS
        )

        average_home_goals = max(
            average_home_goals,
            self.MIN_AVERAGE_GOALS
        )

        base_log_rate = math.log(average_away_goals)
        home_advantage = math.log(
            average_home_goals
            / average_away_goals
        )

        return (
            base_log_rate,
            home_advantage
        )

    def _create_initial_parameters(
        self,
        matches,
        number_of_teams,
        number_of_competitions,
        rho_mode
    ):
        """
        Skapar initiala parameterlägen.
        """
        (
            base_log_rate,
            home_advantage
        ) = self._calculate_initial_goal_levels(
            matches
        )

        parameters = (
            [0.0] * number_of_teams
            + [0.0] * number_of_teams
            + [
                base_log_rate,
                home_advantage
            ]
        )

        if rho_mode == self.RHO_MODE_ESTIMATED:
            parameters += [self.INITIAL_RHO]

        return (
            parameters
            + [0.0] * number_of_competitions
        )

    # --------------------------------------------------
    # Bounds
    # --------------------------------------------------

    def _create_bounds(
        self,
        number_of_teams,
        number_of_competitions,
        rho_mode
    ):
        """
        Skapar bounds för samtliga
        fria parametrar.
        """
        attack_bounds = [
            (
                self.ATTACK_MIN,
                self.ATTACK_MAX
            )
        ] * number_of_teams

        defence_bounds = [
            (
                self.DEFENCE_MIN,
                self.DEFENCE_MAX
            )
        ] * number_of_teams

        competition_bounds = [
            (
                self.COMPETITION_EFFECT_MIN,
                self.COMPETITION_EFFECT_MAX
            )
        ] * number_of_competitions

        parameter_bounds = (
            attack_bounds
            + defence_bounds
            + [
                (
                    self.BASE_LOG_RATE_MIN,
                    self.BASE_LOG_RATE_MAX
                ),
                (
                    self.HOME_ADVANTAGE_MIN,
                    self.HOME_ADVANTAGE_MAX
                )
            ]
        )

        if rho_mode == self.RHO_MODE_ESTIMATED:
            parameter_bounds += [
                (
                    self.RHO_MIN,
                    self.RHO_MAX
                )
            ]

        return parameter_bounds + competition_bounds

    # --------------------------------------------------
    # Constraints
    # --------------------------------------------------

    def _create_constraints(self, number_of_teams):
        """
        Skapar identifieringsvillkoren:

        summa attack = 0
        summa försvar = 0
        """
        attack_start = 0
        attack_end = number_of_teams

        defence_start = attack_end
        defence_end = defence_start + number_of_teams

        return (
            {
                "type": "eq",
                "fun": (
                    lambda parameters: sum(
                        parameters[
                            attack_start:
                            attack_end
                        ]
                    )
                )
            },
            {
                "type": "eq",
                "fun": (
                    lambda parameters: sum(
                        parameters[
                            defence_start:
                            defence_end
                        ]
                    )
                )
            }
        )

    # --------------------------------------------------
    # Parameteruppackning
    # --------------------------------------------------

    def _unpack_parameters(
        self,
        parameters,
        team_ids,
        free_competition_ids,
        reference_competition_id,
        rho_mode
    ):
        """
        Omvandlar parametervektorn till
        namngivna modellparametrar.
        """
        indexes = self._get_parameter_indexes(
            len(team_ids),
            len(free_competition_ids),
            rho_mode
        )

        attack_values = parameters[
            indexes["attack_start"]:
            indexes["attack_end"]
        ]

        defence_values = parameters[
            indexes["defence_start"]:
            indexes["defence_end"]
        ]

        attack = {
            team_id: float(attack_values[index])
            for index, team_id in enumerate(team_ids)
        }

        defence = {
            team_id: float(defence_values[index])
            for index, team_id in enumerate(team_ids)
        }

        base_log_rate = float(
            parameters[indexes["base_log_rate"]]
        )

        home_advantage = float(
            parameters[indexes["home_advantage"]]
        )

        if rho_mode == self.RHO_MODE_ESTIMATED:
            rho = float(
                parameters[indexes["rho"]]
            )
        else:
            rho = self.FIXED_RHO

        competition_values = parameters[
            indexes["competition_start"]:
            indexes["competition_end"]
        ]

        competition_effect = {
            reference_competition_id: 0.0
        }

        for index, competition_id in enumerate(free_competition_ids):
            competition_effect[competition_id] = float(
                competition_values[index]
            )

        return (
            attack,
            defence,
            competition_effect,
            base_log_rate,
            home_advantage,
            rho
        )

    # --------------------------------------------------
    # Likelihood
    # --------------------------------------------------

    def _negative_log_likelihood(
        self,
        parameters,
        match_data,
        number_of_teams,
        number_of_competitions,
        rho_mode
    ):
        """
        Beräknar negativ tidsviktad
        Dixon-Coles log-likelihood med
        vektoriserade NumPy-operationer.
        """
        indexes = self._get_parameter_indexes(
            number_of_teams,
            number_of_competitions,
            rho_mode
        )

        attack = np.asarray(
            parameters[
                indexes["attack_start"]:
                indexes["attack_end"]
            ],
            dtype=np.float64
        )

        defence = np.asarray(
            parameters[
                indexes["defence_start"]:
                indexes["defence_end"]
            ],
            dtype=np.float64
        )

        base_log_rate = parameters[
            indexes["base_log_rate"]
        ]

        home_advantage = parameters[
            indexes["home_advantage"]
        ]

        if rho_mode == self.RHO_MODE_ESTIMATED:
            rho = parameters[
                indexes["rho"]
            ]
        else:
            rho = self.FIXED_RHO

        competition_effects = np.asarray(
            parameters[
                indexes["competition_start"]:
                indexes["competition_end"]
            ],
            dtype=np.float64
        )

        home_team_indexes = match_data["home_team_indexes"]
        away_team_indexes = match_data["away_team_indexes"]
        competition_indexes = match_data["competition_indexes"]
        home_goals = match_data["home_goals"]
        away_goals = match_data["away_goals"]
        weights = match_data["weights"]
        home_log_factorials = match_data["home_log_factorials"]
        away_log_factorials = match_data["away_log_factorials"]

        competition_effect = np.zeros(
            len(home_goals),
            dtype=np.float64
        )

        if number_of_competitions > 0:
            mask = competition_indexes >= 0

            competition_effect[mask] = competition_effects[
                competition_indexes[mask]
            ]

        log_lambda_home = (
            base_log_rate
            + home_advantage
            + competition_effect
            + attack[home_team_indexes]
            - defence[away_team_indexes]
        )

        log_lambda_away = (
            base_log_rate
            + competition_effect
            + attack[away_team_indexes]
            - defence[home_team_indexes]
        )

        lambda_home = np.exp(log_lambda_home)
        lambda_away = np.exp(log_lambda_away)

        home_log_probability = (
            -lambda_home
            + home_goals * log_lambda_home
            - home_log_factorials
        )

        away_log_probability = (
            -lambda_away
            + away_goals * log_lambda_away
            - away_log_factorials
        )

        if rho_mode == self.RHO_MODE_FIXED:
            log_likelihood = np.sum(
                weights
                * (
                    home_log_probability
                    + away_log_probability
                )
            )

            return float(-log_likelihood)

        tau = np.ones(
            len(home_goals),
            dtype=np.float64
        )

        mask_00 = (
            (home_goals == 0)
            & (away_goals == 0)
        )

        mask_01 = (
            (home_goals == 0)
            & (away_goals == 1)
        )

        mask_10 = (
            (home_goals == 1)
            & (away_goals == 0)
        )

        mask_11 = (
            (home_goals == 1)
            & (away_goals == 1)
        )

        tau[mask_00] = (
            1.0
            - lambda_home[mask_00]
            * lambda_away[mask_00]
            * rho
        )

        tau[mask_01] = (
            1.0
            + lambda_home[mask_01]
            * rho
        )

        tau[mask_10] = (
            1.0
            + lambda_away[mask_10]
            * rho
        )

        tau[mask_11] = 1.0 - rho

        if np.any(tau <= 0):
            return self.LARGE_PENALTY

        log_likelihood = np.sum(
            weights
            * (
                home_log_probability
                + away_log_probability
                + np.log(tau)
            )
        )

        return float(-log_likelihood)
