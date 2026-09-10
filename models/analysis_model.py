from datetime import date

from dateutil.relativedelta import relativedelta

from models.analysis.analysis_engine import AnalysisEngine
from models.domains import (
    AnalysisData,
    FormExpectation,
    HeadToHeadStatistics,
    TeamStatistics
)
from mvc import Model


class AnalysisModel(Model):
    """
        Modell som hämtar och förbereder data för matchanalys.
    """

    MODEL_HISTORY_YEARS = 3
    FORM_MATCH_COUNT = 5
    FORM_WEIGHT = 0.0

    H2H_MATCH_COUNT = 5
    H2H_WEIGHT = 0.0

    TRAINING_SCOPE_COUNTRY = "country"
    TRAINING_SCOPE_COMPETITION = "competition"

    DEFAULT_TRAINING_SCOPE = TRAINING_SCOPE_COUNTRY

    def __init__(self, database, soccer_model):
        super().__init__()

        self.database = database
        self.soccer_model = soccer_model
        self.engine = AnalysisEngine()

        self._form_expectation_cache = {}
        self._model_parameters_cache = {}
        self._rho_diagnostics = []

    def create_team_statistics(self, team, season, matches):
        """
            Skapar statistik för ett lag utifrån angivna matcher.
        """
        statistics = TeamStatistics(team=team, season=season)
        statistics.matches_played = 0

        for match in matches:
            if match.home_score is None or match.away_score is None:
                continue

            statistics.matches_played += 1
            home_score = match.home_score
            away_score = match.away_score

            if match.home_team.id == team.id:
                goals_for = home_score
                goals_against = away_score
                statistics.home_matches_played += 1
                statistics.home_goals_for += goals_for
                statistics.home_goals_against += goals_against

                if goals_for > goals_against:
                    statistics.home_wins += 1
                elif goals_for == goals_against:
                    statistics.home_draws += 1
                else:
                    statistics.home_losses += 1

            elif match.away_team.id == team.id:
                goals_for = away_score
                goals_against = home_score
                statistics.away_matches_played += 1
                statistics.away_goals_for += goals_for
                statistics.away_goals_against += goals_against

                if goals_for > goals_against:
                    statistics.away_wins += 1
                elif goals_for == goals_against:
                    statistics.away_draws += 1
                else:
                    statistics.away_losses += 1
            else:
                statistics.matches_played -= 1
                continue

            statistics.goals_for += goals_for
            statistics.goals_against += goals_against

            if goals_for > goals_against:
                statistics.wins += 1
            elif goals_for == goals_against:
                statistics.draws += 1
            else:
                statistics.losses += 1

        return statistics

    def create_season_team_statistics(
        self,
        season,
        *,
        reference_date,
        matches=None
    ):
        """
            Skapar statistik för samtliga lag i den valda säsongen.

            Om matcher anges återanvänds dessa i stället
            för att hämta matcherna på nytt för varje lag.
        """
        teams = self.soccer_model.get_teams_in_season(season.id)

        if matches is None:
            matches = self.soccer_model.get_matches(
                season_id=season.id,
                reference_date=reference_date
            )

        team_matches = {
            team.id: []
            for team in teams
        }

        for match in matches:
            if match.home_team.id in team_matches:
                team_matches[match.home_team.id].append(match)

            if match.away_team.id in team_matches:
                team_matches[match.away_team.id].append(match)

        return {
            team.id: self.create_team_statistics(
                team,
                season,
                team_matches[team.id]
            )
            for team in teams
        }

    def analyze_match(
        self,
        season,
        home_team,
        away_team,
        reference_date=None,
        time_decay=None,
        history_years=None,
        training_scope=None,
        form_match_count=None,
        form_weight=None,
        calculate_form=True,
        h2h_match_count=None,
        h2h_weight=None,
        calculate_h2h=True,
        rho_mode=None
    ):
        """
            Analyserar en match utifrån historiska matcher
            före angivet referensdatum.
        """
        if reference_date is None:
            reference_date = date.today()

        if history_years is None:
            history_years = self.MODEL_HISTORY_YEARS

        if training_scope is None:
            training_scope = self.DEFAULT_TRAINING_SCOPE

        if form_match_count is None:
            form_match_count = self.FORM_MATCH_COUNT

        if form_weight is None:
            form_weight = self.FORM_WEIGHT

        if h2h_match_count is None:
            h2h_match_count = self.H2H_MATCH_COUNT

        if h2h_weight is None:
            h2h_weight = self.H2H_WEIGHT

        start_date = reference_date - relativedelta(years=history_years)

        season_matches = self.soccer_model.get_matches(
            season_id=season.id,
            reference_date=reference_date
        )

        self._validate_matches_before_reference(
            season_matches,
            reference_date,
            "säsongsmatcher"
        )

        home_matches = self._get_team_matches_from_model_matches(
            season_matches,
            home_team.id
        )

        away_matches = self._get_team_matches_from_model_matches(
            season_matches,
            away_team.id
        )

        model_matches = self._get_model_matches(
            season=season,
            start_date=start_date,
            reference_date=reference_date,
            training_scope=training_scope
        )

        home_model_matches = self._get_team_matches_from_model_matches(
            model_matches,
            home_team.id
        )

        away_model_matches = self._get_team_matches_from_model_matches(
            model_matches,
            away_team.id
        )

        team_model_matches = {
            home_team.id: home_model_matches,
            away_team.id: away_model_matches
        }

        home_form_matches = []
        away_form_matches = []
        form_expectations = {}

        if calculate_form:
            home_form_matches = self._get_recent_form_matches(
                home_model_matches,
                form_match_count
            )

            away_form_matches = self._get_recent_form_matches(
                away_model_matches,
                form_match_count
            )

            form_matches = {
                match.id: match
                for match in home_form_matches + away_form_matches
            }

            form_expectations = self._get_form_expectations(
                form_matches.values(),
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                rho_mode=rho_mode
            )

        season_statistics = self.get_season_statistics(
            season_id=season.id,
            reference_date=reference_date
        )

        season_team_statistics = self.create_season_team_statistics(
            season=season,
            reference_date=reference_date,
            matches=season_matches
        )

        home_statistics = season_team_statistics[home_team.id]
        away_statistics = season_team_statistics[away_team.id]

        h2h_statistics = self.get_head_to_head_statistics(
            team_id=home_team.id,
            opponent_id=away_team.id,
            reference_date=reference_date
        )

        h2h_matches = []
        h2h_expectations = {}

        if calculate_h2h:
            h2h_matches = self._get_recent_h2h_matches(
                home_team.id,
                away_team.id,
                reference_date,
                h2h_match_count
            )

            h2h_expectations = self._get_form_expectations(
                h2h_matches,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                rho_mode=rho_mode
            )

        parameters = self._get_model_parameters(
            season=season,
            model_matches=model_matches,
            reference_date=reference_date,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=rho_mode
        )

        data = AnalysisData(
            season=season,
            home_team=home_team,
            away_team=away_team,
            reference_date=reference_date,
            home_matches=home_matches,
            away_matches=away_matches,
            season_matches=season_matches,
            model_matches=model_matches,
            team_model_matches=team_model_matches,
            season_statistics=season_statistics,
            season_team_statistics=season_team_statistics,
            home_statistics=home_statistics,
            away_statistics=away_statistics,
            h2h_statistics=h2h_statistics
        )

        return self.engine.analyze_match(
            data,
            time_decay=time_decay,
            form_weight=form_weight,
            calculate_form=calculate_form,
            home_form_matches=home_form_matches,
            away_form_matches=away_form_matches,
            form_expectations=form_expectations,
            h2h_weight=h2h_weight,
            calculate_h2h=calculate_h2h,
            h2h_matches=h2h_matches,
            h2h_expectations=h2h_expectations,
            parameters=parameters
        )

    def _get_model_matches(
        self,
        *,
        season,
        start_date,
        reference_date,
        training_scope
    ):
        """
            Hämtar Dixon-Coles-modellens matcher
            för vald omfattning av träningsdata.
        """
        if training_scope == self.TRAINING_SCOPE_COUNTRY:
            matches = self.soccer_model.get_country_matches_between_dates(
                season.competition.country,
                start_date,
                reference_date
            )

        elif training_scope == self.TRAINING_SCOPE_COMPETITION:
            matches = self.soccer_model.get_competition_matches_between_dates(
                season.competition.id,
                start_date,
                reference_date
            )

        else:
            raise ValueError(
                f"Okänd omfattning för träningsdata: {training_scope}"
            )

        self._validate_matches_before_reference(
            matches,
            reference_date,
            "Dixon-Coles träningsdata"
        )

        return matches

    @staticmethod
    def _validate_matches_before_reference(
        matches,
        reference_date,
        source
    ):
        """
            Säkerställer att inga matcher från referensdatumet
            eller framtiden används i en historisk analys.
        """
        invalid_matches = [
            match
            for match in matches
            if (
                match.match_date is not None
                and match.match_date >= reference_date
            )
        ]

        if not invalid_matches:
            return

        first_match = min(
            invalid_matches,
            key=lambda match: match.match_date
        )

        raise ValueError(
            "Framtidsläcka upptäckt i "
            f"{source}: match {first_match.id} har datum "
            f"{first_match.match_date}, men referensdatum är "
            f"{reference_date}."
        )

    @staticmethod
    def _get_team_matches_from_model_matches(model_matches, team_id):
        """
            Filtrerar fram ett lags matcher från
            Dixon-Coles-modellens träningsdata.
        """
        return [
            match
            for match in model_matches
            if (
                match.home_team.id == team_id
                or match.away_team.id == team_id
            )
        ]

    def _get_model_parameters(
        self,
        *,
        season,
        model_matches,
        reference_date,
        time_decay,
        history_years,
        training_scope,
        rho_mode=None
    ):
        """
            Hämtar eller skattar Dixon-Coles-parametrar.

            Parametrarna återanvänds när samma modell,
            referensdatum och hyperparametrar används igen.
        """
        cache_key = (
            season.competition.id,
            reference_date,
            time_decay,
            history_years,
            training_scope,
            rho_mode
        )

        if cache_key not in self._model_parameters_cache:
            parameters = self.engine.fit_model(
                model_matches,
                reference_date,
                season.competition.id,
                time_decay=time_decay,
                rho_mode=rho_mode
            )

            self._model_parameters_cache[cache_key] = parameters

            self._rho_diagnostics.append(
                {
                    "reference_date": reference_date,
                    "rho": parameters.rho,
                    "rho_mode": rho_mode,
                    "matches_used": parameters.matches_used
                }
            )

        return self._model_parameters_cache[cache_key]

    def clear_rho_diagnostics(self):
        """
            Rensar insamlade rho-värden.
        """
        self._rho_diagnostics.clear()

    def get_rho_diagnostics(self):
        """
            Returnerar insamlade rho-värden.
        """
        return list(self._rho_diagnostics)

    def clear_analysis_caches(self):
        """
            Tömmer analysens cache.

            Används om underliggande matchdata ändras
            medan samma AnalysisModel-instans lever vidare.
        """
        self._form_expectation_cache.clear()
        self._model_parameters_cache.clear()

    def get_season_statistics(self, season_id, reference_date=None):
        """
            Hämtar statistik för en säsong.
            Om reference_date används, så hämtas bara
            statistik före det datumet.
        """
        return self.database.season_repository.get_season_statistics(
            season_id=season_id,
            reference_date=reference_date
        )

    def get_head_to_head_statistics(
        self,
        team_id,
        opponent_id,
        *,
        reference_date=None
    ):
        """
            Beräknar statistik för inbördes möten.
        """
        matches = self.soccer_model.get_head_to_head_matches(
            home_team_id=team_id,
            away_team_id=opponent_id,
            reference_date=reference_date
        )

        if reference_date is not None:
            self._validate_matches_before_reference(
                matches,
                reference_date,
                "H2H-statistik"
            )

        home_wins = 0
        home_draws = 0
        home_losses = 0
        home_goals = 0
        opponent_goals = 0
        played_matches = 0

        for match in matches:
            if match.home_score is None or match.away_score is None:
                continue

            played_matches += 1

            if match.home_team.id == team_id:
                team_goals = match.home_score
                opponent_match_goals = match.away_score
            elif match.away_team.id == team_id:
                team_goals = match.away_score
                opponent_match_goals = match.home_score
            else:
                continue

            home_goals += team_goals
            opponent_goals += opponent_match_goals

            if team_goals > opponent_match_goals:
                home_wins += 1
            elif team_goals == opponent_match_goals:
                home_draws += 1
            else:
                home_losses += 1

        return HeadToHeadStatistics(
            matches=played_matches,
            home_wins=home_wins,
            home_draws=home_draws,
            home_losses=home_losses,
            home_score=f"{home_goals} – {opponent_goals}",
            away_wins=home_losses,
            away_draws=home_draws,
            away_losses=home_wins,
            away_score=f"{opponent_goals} – {home_goals}"
        )

    def _get_recent_h2h_matches(
        self,
        home_team_id,
        away_team_id,
        reference_date,
        h2h_match_count
    ):
        """
            Hämtar de senaste färdigspelade
            inbördes mötena före referensdatumet.
        """
        matches = self.soccer_model.get_head_to_head_matches(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            reference_date=reference_date
        )

        self._validate_matches_before_reference(
            matches,
            reference_date,
            "H2H-matcher"
        )

        completed_matches = [
            match
            for match in matches
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date is not None
                and match.match_date < reference_date
            )
        ]

        completed_matches.sort(
            key=lambda match: match.match_date,
            reverse=True
        )

        return completed_matches[:h2h_match_count]

    @staticmethod
    def _get_recent_form_matches(matches, form_match_count):
        """
            Hämtar de senaste färdigspelade
            matcherna som används för form.
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

        return completed_matches[:form_match_count]

    def _get_form_expectations(
        self,
        matches,
        *,
        time_decay,
        history_years,
        training_scope,
        rho_mode
    ):
        """
            Beräknar förväntade resultat inför
            de historiska formmatcherna.
        """
        expectations = {}

        for match in matches:
            expectations[match.id] = self._calculate_form_expectation(
                match,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                rho_mode=rho_mode
            )

        return expectations

    def _calculate_form_expectation(
        self,
        match,
        *,
        time_decay,
        history_years,
        training_scope,
        rho_mode
    ):
        """
            Beräknar det förväntade resultatet
            inför en historisk match utan att
            använda form.

            Endast Dixon-Coles-delarna som krävs för
            1X2 beräknas, vilket undviker full matchanalys.
        """
        cache_key = (
            match.id,
            time_decay,
            history_years,
            training_scope,
            rho_mode
        )

        if cache_key in self._form_expectation_cache:
            return self._form_expectation_cache[cache_key]

        history_start_date = (
            match.match_date
            - relativedelta(years=history_years)
        )

        model_matches = self._get_model_matches(
            season=match.season,
            start_date=history_start_date,
            reference_date=match.match_date,
            training_scope=training_scope
        )

        parameters = self._get_model_parameters(
            season=match.season,
            model_matches=model_matches,
            reference_date=match.match_date,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=rho_mode
        )

        (
            probability_1,
            probability_x,
            probability_2
        ) = self.engine.calculate_match_result_probabilities(
            parameters=parameters,
            home_team_id=match.home_team.id,
            away_team_id=match.away_team.id,
            competition_id=match.season.competition.id
        )

        home_expected_result = probability_1 + 0.5 * probability_x
        away_expected_result = probability_2 + 0.5 * probability_x

        expectation = FormExpectation(
            home_expected_result=home_expected_result,
            away_expected_result=away_expected_result
        )

        self._form_expectation_cache[cache_key] = expectation

        return expectation
