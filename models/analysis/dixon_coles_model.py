import math

from scipy.optimize import minimize

from models.domains import DixonColesParameters


class DixonColesModel:
    """
        Gemensam Dixon-Coles-modell för flera tävlingar.
        Attack, försvar, hemmafördel, rho och tävlingseffekter skattas samtidigt.
    """

    # --------------------------------------------------
    # Tidsvikt
    # --------------------------------------------------

    TIME_DECAY = 0.003

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
    # Publikt gränssnitt
    # --------------------------------------------------

    def fit(
        self,
        matches,
        reference_date,
        reference_competition_id
    ):
        """
            Anpassar Dixon-Coles-modellen gemensamt till samtliga matcher.
        """
        completed_matches = self._get_completed_matches(
            matches,
            reference_date
        )

        if not completed_matches:
            raise ValueError(
                "Det finns inga färdigspelade matcher för Dixon-Coles-modellen."
            )

        team_ids = self._get_team_ids(completed_matches)
        competition_ids = self._get_competition_ids(completed_matches)

        if len(team_ids) < 2:
            raise ValueError("För få lag för Dixon-Coles-modellen.")

        if reference_competition_id not in competition_ids:
            raise ValueError("Referenstävlingen saknas i modellens matcher.")

        free_competition_ids = [
            competition_id
            for competition_id in competition_ids
            if competition_id != reference_competition_id
        ]

        initial_parameters = (
            self._create_initial_parameters(
                completed_matches,
                len(team_ids),
                len(free_competition_ids)
            )
        )

        bounds = self._create_bounds(
            len(team_ids),
            len(free_competition_ids)
        )

        constraints = self._create_constraints(len(team_ids))

        result = minimize(
            self._negative_log_likelihood,
            initial_parameters,
            args=(
                completed_matches,
                team_ids,
                free_competition_ids,
                reference_competition_id,
                reference_date
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

        if not result.success:
            raise RuntimeError(
                f"Dixon-Coles-optimeringen misslyckades: {result.message}")

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
            reference_competition_id
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
            Beräknar förväntat antal mål från skattade parametrar.
        """
        # Hemmalaget saknas i Dixon-Coles-modellen.
        if home_team_id not in parameters.attack:
            raise ValueError("Hemmalaget saknas i Dixon-Coles-modellen.")

        if away_team_id not in parameters.attack:
            raise ValueError("Bortalaget saknas i Dixon-Coles-modellen.")

        competition_effect = parameters.competition_effect.get(
            competition_id,
            0.0
        )

        # Hemma
        lambda_home = math.exp(
            parameters.base_log_rate
            + parameters.home_advantage
            + competition_effect
            + parameters.attack[
                home_team_id
            ]
            - parameters.defence[
                away_team_id
            ]
        )

        # Borta
        lambda_away = math.exp(
            parameters.base_log_rate
            + competition_effect
            + parameters.attack[
                away_team_id
            ]
            - parameters.defence[home_team_id]
        )

        return (lambda_home, lambda_away)

    # --------------------------------------------------
    # Matcher
    # --------------------------------------------------

    def _get_completed_matches(
        self,
        matches,
        reference_date
    ):
        """
            Returnerar färdigspelade matcher före referensdatumet.
        """
        return [
            match
            for match in matches
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date
                < reference_date
            )
        ]

    def _get_team_ids(
        self,
        matches
    ):
        """
            Returnerar alla lag-id:n som finns i datamängden.
        """
        team_ids = set()

        for match in matches:
            team_ids.add(match.home_team.id)
            team_ids.add(match.away_team.id)

        return sorted(team_ids)

    def _get_competition_ids(
        self,
        matches
    ):
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
    # Parameterindex
    # --------------------------------------------------

    def _get_parameter_indexes(
        self,
        number_of_teams,
        number_of_competitions
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

        rho_index = home_advantage_index + 1
        competition_start = rho_index + 1
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

    def _calculate_initial_goal_levels(
        self,
        matches
    ):
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

        average_away_goals = max(average_away_goals, self.MIN_AVERAGE_GOALS)
        average_home_goals = max(average_home_goals, self.MIN_AVERAGE_GOALS)

        # Bortalagens målsnitt används som initial gemensam grundnivå.
        base_log_rate = math.log(average_away_goals)

        # Skillnaden mellan hemma och borta blir initial hemmafördel.
        home_advantage = math.log(average_home_goals / average_away_goals)

        return (base_log_rate, home_advantage)

    def _create_initial_parameters(
        self,
        matches,
        number_of_teams,
        number_of_competitions
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

        return (
            [0.0] * number_of_teams
            + [0.0] * number_of_teams
            + [
                base_log_rate,
                home_advantage,
                self.INITIAL_RHO
            ]
            + [0.0] * number_of_competitions
        )

    # --------------------------------------------------
    # Bounds
    # --------------------------------------------------

    def _create_bounds(
        self,
        number_of_teams,
        number_of_competitions
    ):
        """
            Skapar bounds för samtliga fria parametrar.
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

        return (
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
                ),
                (
                    self.RHO_MIN,
                    self.RHO_MAX
                )
            ]
            + competition_bounds
        )

    # --------------------------------------------------
    # Constraints
    # --------------------------------------------------

    def _create_constraints(
        self,
        number_of_teams
    ):
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
                "fun": lambda parameters: sum(
                    parameters[
                        attack_start:
                        attack_end
                    ]
                )
            },
            {
                "type": "eq",
                "fun": lambda parameters: sum(
                    parameters[
                        defence_start:
                        defence_end
                    ]
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
        reference_competition_id
    ):
        """
            Omvandlar parametervektorn till namngivna modellparametrar.
        """
        indexes = (
            self._get_parameter_indexes(
                len(team_ids),
                len(free_competition_ids)
            )
        )

        attack_values = parameters[
            indexes["attack_start"]:indexes["attack_end"]
        ]

        defence_values = parameters[
            indexes["defence_start"]:indexes["defence_end"]
        ]

        attack = {
            team_id: float(attack_values[index])
            for index, team_id in enumerate(
                team_ids
            )
        }

        defence = {
            team_id: float(
                defence_values[index]
            )
            for index, team_id in enumerate(
                team_ids
            )
        }

        base_log_rate = float(
            parameters[
                indexes["base_log_rate"]
            ]
        )

        home_advantage = float(
            parameters[
                indexes["home_advantage"]
            ]
        )

        rho = float(
            parameters[
                indexes["rho"]
            ]
        )

        competition_values = parameters[indexes["competition_start"]:indexes["competition_end"]]
        competition_effect = {reference_competition_id: 0.0}

        for index, competition_id in enumerate(
            free_competition_ids
        ):
            competition_effect[
                competition_id
            ] = float(competition_values[index])

        return (
            attack,
            defence,
            competition_effect,
            base_log_rate,
            home_advantage,
            rho
        )

    # --------------------------------------------------
    # Lambda
    # --------------------------------------------------

    def _calculate_expected_goals(
        self,
        *,
        match,
        attack,
        defence,
        competition_effect,
        base_log_rate,
        home_advantage
    ):
        """
            Beräknar lambda för en historisk match.
        """
        home_team_id = match.home_team.id
        away_team_id = match.away_team.id

        competition_id = match.season.competition.id

        effect = (
            competition_effect.get(
                competition_id,
                0.0
            )
        )

        lambda_home = math.exp(
            base_log_rate
            + home_advantage
            + effect
            + attack[
                home_team_id
            ]
            - defence[
                away_team_id
            ]
        )

        lambda_away = math.exp(
            base_log_rate
            + effect
            + attack[
                away_team_id
            ]
            - defence[
                home_team_id
            ]
        )

        return (lambda_home, lambda_away)

    # --------------------------------------------------
    # Poisson
    # --------------------------------------------------

    def _calculate_poisson_log_probability(
        self,
        goals,
        lambda_value
    ):
        """
            Returnerar logaritmen av Poisson-sannolikheten.
        """
        return (
            -lambda_value
            + goals
            * math.log(
                lambda_value
            )
            - math.lgamma(
                goals + 1
            )
        )

    # --------------------------------------------------
    # Dixon-Coles tau
    # --------------------------------------------------

    def _calculate_tau(
        self,
        home_goals,
        away_goals,
        lambda_home,
        lambda_away,
        rho
    ):
        """
            Beräknar Dixon-Coles lågmålskorrigering.
        """
        if home_goals == 0 and away_goals == 0:
            return 1 - lambda_home * lambda_away * rho

        if home_goals == 0 and away_goals == 1:
            return 1 + lambda_home * rho

        if home_goals == 1 and away_goals == 0:
            return 1 + lambda_away * rho

        if home_goals == 1 and away_goals == 1:
            return 1 - rho
        return 1.0

    # --------------------------------------------------
    # Tidsvikt
    # --------------------------------------------------

    def _calculate_time_weight(
        self,
        match_date,
        reference_date
    ):
        """
            Nyare matcher får större vikt.
        """
        days_old = (reference_date - match_date).days

        if days_old < 0:
            return 0.0

        return math.exp(-self.TIME_DECAY * days_old)

    # --------------------------------------------------
    # Likelihood
    # --------------------------------------------------

    def _negative_log_likelihood(
        self,
        parameters,
        matches,
        team_ids,
        free_competition_ids,
        reference_competition_id,
        reference_date
    ):
        """
            Beräknar negativ tidsviktad
            Dixon-Coles log-likelihood.
        """
        (
            attack,
            defence,
            competition_effect,
            base_log_rate,
            home_advantage,
            rho
        ) = self._unpack_parameters(
            parameters,
            team_ids,
            free_competition_ids,
            reference_competition_id
        )

        log_likelihood = 0.0

        for match in matches:
            (
                lambda_home,
                lambda_away
            ) = self._calculate_expected_goals(
                match=match,
                attack=attack,
                defence=defence,
                competition_effect=competition_effect,
                base_log_rate=base_log_rate,
                home_advantage=home_advantage
            )

            tau = self._calculate_tau(
                match.home_score,
                match.away_score,
                lambda_home,
                lambda_away,
                rho
            )

            if tau <= 0:
                return self.LARGE_PENALTY

            home_log_probability = (
                self._calculate_poisson_log_probability(
                    match.home_score,
                    lambda_home
                )
            )

            away_log_probability = (
                self._calculate_poisson_log_probability(
                    match.away_score,
                    lambda_away
                )
            )

            weight = (
                self._calculate_time_weight(
                    match.match_date,
                    reference_date
                )
            )

            log_likelihood += (
                weight
                * (
                    home_log_probability
                    + away_log_probability
                    + math.log(tau)
                )
            )

        return -log_likelihood
