import math
import statistics
import time
from types import SimpleNamespace

import numpy as np

from models.analysis.backtest_engine import BacktestEngine
from models.analysis.backtest_parallel_runner import BacktestParallelRunner
from models.analysis.backtest_utils import (
    evaluate_common_predictions,
    filter_predictions,
    get_common_prediction_keys,
    get_result_metrics,
    is_cancelled,
    is_completed_match,
    report_progress
)
from models.analysis.dixon_coles_model import DixonColesModel
from models.analysis.probability_calibration_model import (
    ProbabilityCalibrationModel
)
from models.domains import (
    BacktestPrediction,
    CalibrationModelBacktestResult,
    FormBacktestResult,
    HistoryYearsBacktestResult,
    TimeDecayBacktestResult,
    TrainingScopeBacktestResult
)
from mvc import Model


class BacktestModel(Model):
    """
        Genomför historiska backtester av matchanalysmodellen.
    """

    # --------------------------------------------------
    # Konstanter
    # --------------------------------------------------

    IGNORED_ANALYSIS_ERRORS = {
        "Hemmalaget saknas i Dixon-Coles-modellen.",
        "Bortalaget saknas i Dixon-Coles-modellen.",
        "Det finns inga färdigspelade matcher för Dixon-Coles-modellen.",
        "För få lag för Dixon-Coles-modellen.",
        "Referenstävlingen saknas i modellens matcher."
    }

    DEFAULT_WORKER_COUNTS = (1, 2, 4, 8, 14, 28)
    RHO_BOUND_TOLERANCE = 0.001

    CALIBRATION_NONE = "none"
    CALIBRATION_GLOBAL = "global"
    CALIBRATION_LEAGUE = "league"

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self, *, soccer_model, analysis_model):
        """
            Initierar backtestmodellen.
        """
        self.soccer_model = soccer_model
        self.analysis_model = analysis_model
        self.engine = BacktestEngine()

        self.parallel_runner = BacktestParallelRunner(
            soccer_model=soccer_model,
            backtest_model_type=type(self)
        )

    # --------------------------------------------------
    # Hjälpfunktioner
    # --------------------------------------------------

    def _get_effective_setting(self, value, getter_name, fallback=None):
        """
            Returnerar uttryckligen angivet värde eller modellens standardvärde.
        """
        if value is not None:
            return value

        getter = getattr(self.analysis_model, getter_name, None)

        if getter is not None:
            return getter()

        return fallback

    # --------------------------------------------------
    # Enskilt backtest
    # --------------------------------------------------

    def run(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        form_match_count=None,
        form_weight=None,
        h2h_match_count=None,
        h2h_weight=None,
        rho_mode=None,
        home_advantage_mode=None,
        should_cancel=None,
        matches=None,
        progress_callback=None,
        progress_offset=0,
        progress_total=None,
        return_predictions=False
    ):
        """
            Backtestar modellen på färdigspelade matcher i vald säsong.
        """
        if matches is None:
            matches = self.soccer_model.get_matches(season_id=season.id)

        if progress_total is None:
            progress_total = len(matches)

        effective_time_decay = self._get_effective_setting(
            time_decay,
            "get_time_decay",
            DixonColesModel.TIME_DECAY
        )

        effective_history_years = self._get_effective_setting(
            history_years,
            "get_history_years"
        )

        effective_training_scope = self._get_effective_setting(
            training_scope,
            "get_training_scope"
        )

        effective_form_match_count = self._get_effective_setting(
            form_match_count,
            "get_form_match_count"
        )

        effective_form_weight = self._get_effective_setting(
            form_weight,
            "get_form_weight",
            0.0
        )

        effective_h2h_match_count = self._get_effective_setting(
            h2h_match_count,
            "get_h2h_match_count"
        )

        effective_h2h_weight = self._get_effective_setting(
            h2h_weight,
            "get_h2h_weight",
            0.0
        )

        effective_rho_mode = self._get_effective_setting(
            rho_mode,
            "get_rho_mode",
            DixonColesModel.DEFAULT_RHO_MODE
        )

        effective_home_advantage_mode = (
            home_advantage_mode
            if home_advantage_mode is not None
            else DixonColesModel.DEFAULT_HOME_ADVANTAGE_MODE
        )

        calculate_form = effective_form_weight != 0.0
        calculate_h2h = effective_h2h_weight != 0.0

        predictions = []

        for index, match in enumerate(matches, start=1):
            if is_cancelled(should_cancel):
                return None

            if not is_completed_match(match):
                report_progress(
                    progress_callback,
                    progress_offset + index,
                    progress_total
                )
                continue

            try:
                analysis = self.analysis_model.analyze_match(
                    season=match.season,
                    home_team=match.home_team,
                    away_team=match.away_team,
                    reference_date=match.match_date,
                    time_decay=effective_time_decay,
                    history_years=effective_history_years,
                    training_scope=effective_training_scope,
                    form_match_count=effective_form_match_count,
                    form_weight=effective_form_weight,
                    calculate_form=calculate_form,
                    h2h_match_count=effective_h2h_match_count,
                    h2h_weight=effective_h2h_weight,
                    calculate_h2h=calculate_h2h,
                    rho_mode=effective_rho_mode,
                    home_advantage_mode=effective_home_advantage_mode
                )

            except ValueError as error:
                if str(error) not in self.IGNORED_ANALYSIS_ERRORS:
                    raise

                report_progress(
                    progress_callback,
                    progress_offset + index,
                    progress_total
                )
                continue

            if is_cancelled(should_cancel):
                return None

            predictions.append(
                self._create_prediction(match, analysis)
            )

            report_progress(
                progress_callback,
                progress_offset + index,
                progress_total
            )

        if is_cancelled(should_cancel):
            return None

        if not predictions:
            raise ValueError(
                "Det finns inga prognoser att utvärdera."
            )

        if return_predictions:
            return predictions

        return self.engine.evaluate(predictions)

    # --------------------------------------------------
    # Kalibreringsmodell
    # --------------------------------------------------

    def run_calibration_model_comparison(
        self,
        *,
        season,
        time_decay,
        history_years,
        training_scope,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför okalibrerade sannolikheter med global
            och ligaspecifik sannolikhetskalibrering.

            Global kalibrering använder tidigare säsonger
            från samtliga tävlingar i samma land.

            Ligaspecifik kalibrering använder endast
            tidigare säsonger från samma tävling.

            Endast historiska säsonger används för att
            undvika framtidsläckage.
        """
        test_matches = self.soccer_model.get_matches(season_id=season.id)

        global_seasons, league_seasons = (
            self._get_calibration_training_seasons(test_season=season)
        )

        if not global_seasons:
            raise ValueError(
                "Det finns inga tidigare säsonger "
                "för global kalibrering."
            )

        if not league_seasons:
            raise ValueError(
                "Det finns inga tidigare säsonger "
                "i den valda ligan för kalibrering."
            )

        matches_by_season = {
            training_season.id: self.soccer_model.get_matches(
                season_id=training_season.id
            )
            for training_season in global_seasons
        }

        total_steps = (
            len(test_matches)
            + sum(len(matches) for matches in matches_by_season.values())
        )

        if total_steps <= 0:
            raise ValueError(
                "Det finns inga matcher att använda "
                "i kalibreringsjämförelsen."
            )

        # Testsäsong.

        self.analysis_model.clear_analysis_caches()

        test_predictions = self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            should_cancel=should_cancel,
            matches=test_matches,
            progress_callback=progress_callback,
            progress_offset=0,
            progress_total=total_steps,
            return_predictions=True
        )

        if test_predictions is None:
            return None

        if is_cancelled(should_cancel):
            return None

        # Historiska prognoser.

        predictions_by_season = {}
        progress_offset = len(test_matches)

        for training_season in global_seasons:
            if is_cancelled(should_cancel):
                return None

            self.analysis_model.clear_analysis_caches()

            matches = matches_by_season[training_season.id]

            predictions = self.run(
                season=training_season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                form_match_count=form_match_count,
                form_weight=form_weight,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=progress_offset,
                progress_total=total_steps,
                return_predictions=True
            )

            if predictions is None:
                return None

            predictions_by_season[training_season.id] = predictions
            progress_offset += len(matches)

        if is_cancelled(should_cancel):
            return None

        # Träningsmängder.

        global_predictions = self._combine_season_predictions(
            global_seasons,
            predictions_by_season
        )

        league_predictions = self._combine_season_predictions(
            league_seasons,
            predictions_by_season
        )

        if not global_predictions:
            raise ValueError(
                "Det finns inga prognoser för global kalibrering."
            )

        if not league_predictions:
            raise ValueError(
                "Det finns inga prognoser för ligaspecifik kalibrering."
            )

        # Ingen kalibrering.

        raw_result = self.engine.evaluate(test_predictions)

        none_result = CalibrationModelBacktestResult(
            calibration_model=self.CALIBRATION_NONE,
            calibration_model_label="Ingen",
            beta=1.0,
            training_matches=0,
            training_seasons=0,
            **get_result_metrics(raw_result)
        )

        # Global kalibrering.

        global_result = self._evaluate_calibration_variant(
            calibration_model=self.CALIBRATION_GLOBAL,
            calibration_model_label="Global",
            training_predictions=global_predictions,
            training_season_count=len(global_seasons),
            test_predictions=test_predictions
        )

        # Ligaspecifik kalibrering.

        league_result = self._evaluate_calibration_variant(
            calibration_model=self.CALIBRATION_LEAGUE,
            calibration_model_label="Liga",
            training_predictions=league_predictions,
            training_season_count=len(league_seasons),
            test_predictions=test_predictions
        )

        return [
            none_result,
            global_result,
            league_result
        ]

    def _get_calibration_training_seasons(self, *, test_season):
        """
            Returnerar historiska säsonger för global
            respektive ligaspecifik kalibrering.

            Global:
            Alla tidigare säsonger från samma land.

            Liga:
            Alla tidigare säsonger från samma tävling.
        """
        seasons = self.soccer_model.get_all_seasons()

        global_seasons = []
        league_seasons = []

        for candidate_season in seasons:
            if not self._is_previous_season(
                candidate_season,
                test_season
            ):
                continue

            if (
                candidate_season.competition.country.id
                != test_season.competition.country.id
            ):
                continue

            global_seasons.append(candidate_season)

            if (
                candidate_season.competition.id
                == test_season.competition.id
            ):
                league_seasons.append(candidate_season)

        return (
            self._get_unique_seasons(global_seasons),
            self._get_unique_seasons(league_seasons)
        )

    @staticmethod
    def _is_previous_season(candidate_season, test_season):
        """
            Kontrollerar att kandidatsäsongen ligger
            före testsäsongen.
        """
        return (
            candidate_season.id != test_season.id
            and candidate_season.end_year <= test_season.start_year
        )

    def _evaluate_calibration_variant(
        self,
        *,
        calibration_model,
        calibration_model_label,
        training_predictions,
        training_season_count,
        test_predictions
    ):
        """
            Skattar kalibreringsparametern från historiska
            prognoser och utvärderar den på testsäsongen.
        """
        if not training_predictions:
            raise ValueError(
                f"Det finns inga träningsprognoser för "
                f"{calibration_model_label.lower()} kalibrering."
            )

        calibrator = ProbabilityCalibrationModel()
        beta = calibrator.fit(training_predictions)
        calibrated_predictions = calibrator.transform(test_predictions)
        result = self.engine.evaluate(calibrated_predictions)

        return CalibrationModelBacktestResult(
            calibration_model=calibration_model,
            calibration_model_label=calibration_model_label,
            beta=beta,
            training_matches=len(training_predictions),
            training_seasons=training_season_count,
            **get_result_metrics(result)
        )

    @staticmethod
    def _get_unique_seasons(seasons):
        """
            Tar bort dubbletter och sorterar säsongerna
            kronologiskt och därefter efter tävling.
        """
        unique_seasons = {
            season.id: season
            for season in seasons
        }

        return sorted(
            unique_seasons.values(),
            key=lambda season: (
                season.start_year,
                season.end_year,
                season.competition.id
            )
        )

    @staticmethod
    def _combine_season_predictions(seasons, predictions_by_season):
        """
            Slår samman prognoser från angivna säsonger.
        """
        predictions = []

        for season in seasons:
            predictions.extend(predictions_by_season.get(season.id, []))

        return predictions

    # --------------------------------------------------
    # Rho-jämförelse
    # --------------------------------------------------

    def run_rho_comparison(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför fritt skattad rho med rho låst till 0.0
            på samma matcher.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        total_steps = len(matches) * 2

        estimated_predictions = self._run_rho_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=DixonColesModel.RHO_MODE_ESTIMATED,
            progress_offset=0,
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if estimated_predictions is None:
            return None

        zero_predictions = self._run_rho_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            rho_mode=DixonColesModel.RHO_MODE_FIXED,
            progress_offset=len(matches),
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if zero_predictions is None:
            return None

        results = evaluate_common_predictions(
            self.engine,
            [estimated_predictions, zero_predictions],
            "Det finns inga gemensamma prognoser för rho-jämförelsen."
        )

        return [
            self._create_rho_comparison_result(
                "Skattad",
                results[0]
            ),
            self._create_rho_comparison_result(
                "0.0",
                results[1]
            )
        ]

    def _run_rho_variant(
        self,
        *,
        season,
        matches,
        time_decay,
        history_years,
        training_scope,
        rho_mode,
        progress_offset,
        progress_total,
        should_cancel,
        progress_callback
    ):
        """
            Kör en av rho-varianterna med rensad analyscache.
        """
        self.analysis_model.clear_analysis_caches()

        return self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=rho_mode,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=progress_offset,
            progress_total=progress_total,
            return_predictions=True
        )

    @staticmethod
    def _create_rho_comparison_result(label, result):
        """
            Skapar ett tabellkompatibelt resultat för rho-jämförelsen.
        """
        return SimpleNamespace(
            rho_label=label,
            **get_result_metrics(result)
        )

    # --------------------------------------------------
    # Hemmafördels-jämförelse
    # --------------------------------------------------

    def run_home_advantage_comparison(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        form_match_count=None,
        form_weight=None,
        h2h_match_count=None,
        h2h_weight=None,
        rho_mode=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför skattad hemmafördel med hemmafördel låst
            till 0.0 på exakt samma matcher.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        total_steps = len(matches) * 2

        estimated_predictions = self._run_home_advantage_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=(
                DixonColesModel.HOME_ADVANTAGE_MODE_ESTIMATED
            ),
            progress_offset=0,
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if estimated_predictions is None:
            return None

        zero_predictions = self._run_home_advantage_variant(
            season=season,
            matches=matches,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=(
                DixonColesModel.HOME_ADVANTAGE_MODE_FIXED
            ),
            progress_offset=len(matches),
            progress_total=total_steps,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if zero_predictions is None:
            return None

        common_keys = get_common_prediction_keys(
            [
                estimated_predictions,
                zero_predictions
            ]
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma prognoser för "
                "hemmafördels-jämförelsen."
            )

        estimated_predictions = filter_predictions(
            estimated_predictions,
            common_keys
        )

        zero_predictions = filter_predictions(
            zero_predictions,
            common_keys
        )

        results = [
            self.engine.evaluate(
                estimated_predictions
            ),
            self.engine.evaluate(
                zero_predictions
            )
        ]

        return [
            self._create_home_advantage_comparison_result(
                "Skattad",
                results[0],
                estimated_predictions
            ),
            self._create_home_advantage_comparison_result(
                "0.0",
                results[1],
                zero_predictions
            )
        ]

    def _run_home_advantage_variant(
        self,
        *,
        season,
        matches,
        time_decay,
        history_years,
        training_scope,
        form_match_count,
        form_weight,
        h2h_match_count,
        h2h_weight,
        rho_mode,
        home_advantage_mode,
        progress_offset,
        progress_total,
        should_cancel,
        progress_callback
    ):
        """
            Kör en hemmafördelsvariant med rensad analyscache.
        """
        self.analysis_model.clear_analysis_caches()

        return self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_match_count=form_match_count,
            form_weight=form_weight,
            h2h_match_count=h2h_match_count,
            h2h_weight=h2h_weight,
            rho_mode=rho_mode,
            home_advantage_mode=home_advantage_mode,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=progress_offset,
            progress_total=progress_total,
            return_predictions=True
        )

    @staticmethod
    def _create_home_advantage_comparison_result(
        label,
        result,
        predictions
    ):
        """
            Skapar ett tabellkompatibelt resultat
            för hemmafördels-jämförelsen.
        """
        home_advantage_values = [
            prediction.home_advantage
            for prediction in predictions
        ]

        mean_home_advantage = statistics.mean(
            home_advantage_values
        )

        median_home_advantage = statistics.median(
            home_advantage_values
        )

        goal_multiplier = math.exp(
            mean_home_advantage
        )

        return SimpleNamespace(
            home_advantage_label=label,
            home_advantage_mean=mean_home_advantage,
            home_advantage_median=median_home_advantage,
            home_advantage_minimum=min(home_advantage_values),
            home_advantage_maximum=max(home_advantage_values),
            home_advantage_goal_multiplier=goal_multiplier,
            home_advantage_goal_percentage=(
                goal_multiplier - 1.0
            ) * 100.0,
            **get_result_metrics(result)
        )

    # --------------------------------------------------
    # Rho-diagnostik
    # --------------------------------------------------

    def run_rho_diagnostics(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
        should_cancel=None,
        matches=None,
        progress_callback=None
    ):
        """
            Kör ett backtest och sammanställer skattade rho-värden.
        """
        self.analysis_model.clear_analysis_caches()
        self.analysis_model.clear_rho_diagnostics()

        if matches is None:
            matches = self.soccer_model.get_matches(
                season_id=season.id
            )

        completed_matches = [
            match
            for match in matches
            if is_completed_match(match)
        ]

        match_dates = {
            match.match_date
            for match in completed_matches
        }

        result = self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=DixonColesModel.RHO_MODE_ESTIMATED,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback
        )

        if result is None:
            return None

        diagnostics = (
            self.analysis_model.get_rho_diagnostics()
        )

        if not diagnostics:
            raise ValueError(
                "Inga rho-värden samlades in under backtestet."
            )

        return self._create_rho_diagnostics_result(
            result,
            completed_matches,
            match_dates,
            diagnostics
        )

    def _create_rho_diagnostics_result(
        self,
        result,
        completed_matches,
        match_dates,
        diagnostics
    ):
        """
            Skapar sammanställningen för rho-diagnostiken.
        """
        rho_values = [
            item["rho"]
            for item in diagnostics
        ]

        reference_dates = [
            item["reference_date"]
            for item in diagnostics
        ]

        unique_reference_dates = set(
            reference_dates
        )

        missing_reference_dates = sorted(
            match_dates - unique_reference_dates
        )

        extra_reference_dates = sorted(
            unique_reference_dates - match_dates
        )

        model = (
            self.analysis_model.engine.dixon_coles_model
        )

        lower_bound = model.RHO_MIN
        upper_bound = model.RHO_MAX

        lower_bound_count = sum(
            math.isclose(
                rho,
                lower_bound,
                rel_tol=0.0,
                abs_tol=self.RHO_BOUND_TOLERANCE
            )
            for rho in rho_values
        )

        upper_bound_count = sum(
            math.isclose(
                rho,
                upper_bound,
                rel_tol=0.0,
                abs_tol=self.RHO_BOUND_TOLERANCE
            )
            for rho in rho_values
        )

        count = len(rho_values)

        return {
            "backtest_result": result,
            "match_count": len(completed_matches),
            "match_date_count": len(match_dates),
            "count": count,
            "reference_date_count": len(
                unique_reference_dates
            ),
            "duplicate_reference_date_count": (
                count - len(unique_reference_dates)
            ),
            "missing_reference_date_count": len(
                missing_reference_dates
            ),
            "extra_reference_date_count": len(
                extra_reference_dates
            ),
            "missing_reference_dates": missing_reference_dates,
            "extra_reference_dates": extra_reference_dates,
            "minimum": min(rho_values),
            "percentile_05": float(
                np.percentile(rho_values, 5)
            ),
            "mean": statistics.mean(rho_values),
            "median": statistics.median(rho_values),
            "percentile_95": float(
                np.percentile(rho_values, 95)
            ),
            "maximum": max(rho_values),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "lower_bound_count": lower_bound_count,
            "upper_bound_count": upper_bound_count,
            "lower_bound_percentage": (
                lower_bound_count / count * 100.0
            ),
            "upper_bound_percentage": (
                upper_bound_count / count * 100.0
            ),
            "values": diagnostics
        }

    # --------------------------------------------------
    # Prognoser
    # --------------------------------------------------

    @staticmethod
    def _create_prediction(match, analysis):
        """
            Skapar en historisk prognos från matchanalysen.
        """
        match_result = (
            analysis.odds_analysis.match_result
        )

        return BacktestPrediction(
            match_date=match.match_date,
            home_team=match.home_team,
            away_team=match.away_team,
            probability_1=match_result["1"].probability,
            probability_x=match_result["X"].probability,
            probability_2=match_result["2"].probability,
            actual_result=match.result_1x2,
            home_advantage=analysis.home_advantage
        )

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    def run_time_decay_comparison(
        self,
        *,
        season,
        time_decay_values,
        history_years,
        training_scope,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför flera time-decay-värden
            med samma övriga modellparametrar.
        """
        if not time_decay_values:
            raise ValueError(
                "Inga time-decay-värden har angetts."
            )

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight,
                "return_predictions": False
            }
            for time_decay in time_decay_values
        ]

        backtest_results = self.parallel_runner.run(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if backtest_results is None:
            return None

        return [
            TimeDecayBacktestResult(
                time_decay=time_decay,
                **get_result_metrics(result)
            )
            for time_decay, result in zip(
                time_decay_values,
                backtest_results
            )
        ]

    # --------------------------------------------------
    # Historiklängd
    # --------------------------------------------------

    def run_history_years_comparison(
        self,
        *,
        season,
        history_years_values,
        time_decay,
        training_scope,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför flera historiklängder och
            utvärderar gemensamma prognoser.
        """
        if not history_years_values:
            raise ValueError(
                "Inga historiklängder har angetts."
            )

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight,
                "return_predictions": True
            }
            for history_years in history_years_values
        ]

        prediction_sets = self.parallel_runner.run(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if prediction_sets is None:
            return None

        evaluated = evaluate_common_predictions(
            self.engine,
            prediction_sets
        )

        return [
            HistoryYearsBacktestResult(
                history_years=history_years,
                **get_result_metrics(result)
            )
            for history_years, result in zip(
                history_years_values,
                evaluated
            )
        ]

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    def run_training_scope_comparison(
        self,
        *,
        season,
        training_scopes,
        time_decay,
        history_years,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför flera omfattningar av träningsdata.
        """
        if not training_scopes:
            raise ValueError(
                "Inga träningsomfattningar har angetts."
            )

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight,
                "return_predictions": False
            }
            for training_scope in training_scopes
        ]

        backtest_results = self.parallel_runner.run(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if backtest_results is None:
            return None

        return [
            TrainingScopeBacktestResult(
                training_scope=training_scope,
                **get_result_metrics(result)
            )
            for training_scope, result in zip(
                training_scopes,
                backtest_results
            )
        ]

    # --------------------------------------------------
    # Worker-benchmark
    # --------------------------------------------------

    def run_worker_benchmark(
        self,
        *,
        season,
        form_match_count,
        form_weights,
        time_decay,
        history_years,
        training_scope,
        repeat_count=2,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Benchmarkar olika antal workers
            med samma formjämförelse.
        """
        if not form_weights:
            raise ValueError(
                "Det finns inga formvikter för benchmark."
            )

        if form_match_count is None:
            raise ValueError(
                "Antal formmatcher måste anges."
            )

        if repeat_count <= 0:
            raise ValueError(
                "Antal benchmarkkörningar måste "
                "vara större än 0."
            )

        worker_counts = self._get_worker_counts(
            len(form_weights)
        )

        timings = {
            worker_count: []
            for worker_count in worker_counts
        }

        total_runs = (
            len(worker_counts) * repeat_count
        )

        completed_runs = 0

        for repeat_index in range(repeat_count):
            current_worker_counts = (
                worker_counts
                if repeat_index % 2 == 0
                else reversed(worker_counts)
            )

            for worker_count in current_worker_counts:
                if is_cancelled(should_cancel):
                    return None

                start_time = time.perf_counter()

                result = self.run_form_comparison(
                    season=season,
                    form_match_counts=[
                        form_match_count
                    ],
                    form_weights=form_weights,
                    time_decay=time_decay,
                    history_years=history_years,
                    training_scope=training_scope,
                    should_cancel=should_cancel,
                    progress_callback=None,
                    max_workers=worker_count
                )

                if result is None:
                    return None

                timings[worker_count].append(
                    time.perf_counter() - start_time
                )

                completed_runs += 1

                report_progress(
                    progress_callback,
                    completed_runs,
                    total_runs
                )

        return [
            self._create_worker_benchmark_result(
                worker_count,
                timings[worker_count]
            )
            for worker_count in worker_counts
        ]

    def _get_worker_counts(self, task_count):
        """
            Returnerar relevanta worker-antal
            för angivet antal uppgifter.
        """
        worker_counts = [
            worker_count
            for worker_count in self.DEFAULT_WORKER_COUNTS
            if worker_count <= task_count
        ]

        if task_count not in worker_counts:
            worker_counts.append(task_count)

        return sorted(
            set(worker_counts)
        )

    @staticmethod
    def _create_worker_benchmark_result(
        worker_count,
        values
    ):
        """
            Skapar ett resultatobjekt för worker-benchmark.
        """
        return SimpleNamespace(
            worker_count=worker_count,
            run_count=len(values),
            median_seconds=statistics.median(values),
            minimum_seconds=min(values),
            maximum_seconds=max(values),
            timings=tuple(values)
        )

    # --------------------------------------------------
    # Inbördes möten
    # --------------------------------------------------

    def run_h2h_comparison(
        self,
        *,
        season,
        h2h_match_count,
        h2h_weights,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför H2H-vikter och utvärderar
            endast gemensamma prognoser.
        """
        if not h2h_weights:
            raise ValueError(
                "Det finns inga H2H-vikter att jämföra."
            )

        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        completed_matches = [
            match
            for match in matches
            if is_completed_match(match)
        ]

        eligible_matches = [
            match
            for match in completed_matches
            if self._has_required_h2h_history(
                match,
                h2h_match_count
            )
        ]

        excluded_match_count = (
            len(completed_matches)
            - len(eligible_matches)
        )

        if not eligible_matches:
            raise ValueError(
                f"Det finns inga matcher med minst "
                f"{h2h_match_count} tidigare H2H-matcher."
            )

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "h2h_match_count": h2h_match_count,
                "h2h_weight": h2h_weight,
                "return_predictions": True
            }
            for h2h_weight in h2h_weights
        ]

        prediction_sets = self._run_h2h_tasks(
            tasks=tasks,
            eligible_matches=eligible_matches,
            should_cancel=should_cancel,
            progress_callback=progress_callback
        )

        if prediction_sets is None:
            return None

        evaluated = evaluate_common_predictions(
            self.engine,
            prediction_sets,
            "Det finns inga gemensamma prognoser "
            "för H2H-jämförelsen."
        )

        return [
            SimpleNamespace(
                h2h_weight=h2h_weight,
                h2h_eligible_matches=len(
                    eligible_matches
                ),
                h2h_excluded_matches=excluded_match_count,
                h2h_required_matches=h2h_match_count,
                **get_result_metrics(result)
            )
            for h2h_weight, result in zip(
                h2h_weights,
                evaluated
            )
        ]

    def _run_h2h_tasks(
        self,
        *,
        tasks,
        eligible_matches,
        should_cancel,
        progress_callback
    ):
        """
            Kör H2H-jämförelser sekventiellt och återanvänder
            modellparametrar och H2H-förväntningar mellan vikterna.
        """
        prediction_sets = []

        total_steps = (
            len(eligible_matches) * len(tasks)
        )

        self.analysis_model.clear_analysis_caches()

        for task_index, task in enumerate(tasks):
            if is_cancelled(should_cancel):
                return None

            predictions = self.run(
                **task,
                should_cancel=should_cancel,
                matches=eligible_matches,
                progress_callback=progress_callback,
                progress_offset=(
                    task_index * len(eligible_matches)
                ),
                progress_total=total_steps
            )

            if predictions is None:
                return None

            prediction_sets.append(predictions)

        return prediction_sets

    def _has_required_h2h_history(
        self,
        match,
        required_match_count
    ):
        """
            Kontrollerar att matchen har minst
            angivet antal tidigare H2H-matcher.
        """
        h2h_matches = (
            self.soccer_model.get_head_to_head_matches(
                home_team_id=match.home_team.id,
                away_team_id=match.away_team.id,
                reference_date=match.match_date
            )
        )

        completed_h2h_matches = [
            h2h_match
            for h2h_match in h2h_matches
            if (
                is_completed_match(h2h_match)
                and h2h_match.match_date < match.match_date
            )
        ]

        return (
            len(completed_h2h_matches)
            >= required_match_count
        )

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def run_form_match_count_comparison(
        self,
        *,
        season,
        form_match_counts,
        form_weight,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför olika antal formmatcher
            med fast formvikt.
        """
        if not form_match_counts:
            raise ValueError(
                "Det finns inga antal formmatcher att jämföra."
            )

        if form_weight is None:
            raise ValueError(
                "Formvikt måste anges."
            )

        return self.run_form_comparison(
            season=season,
            form_match_counts=form_match_counts,
            form_weights=[form_weight],
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

    def run_form_comparison(
        self,
        *,
        season,
        form_match_counts,
        form_weights,
        time_decay,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Jämför formvikter och utvärderar
            endast gemensamma prognoser.
        """
        if not form_match_counts:
            raise ValueError(
                "Det finns inga antal formmatcher att jämföra."
            )

        if not form_weights:
            raise ValueError(
                "Det finns inga formvikter att jämföra."
            )

        combinations = [
            (
                form_match_count,
                form_weight
            )
            for form_match_count in form_match_counts
            for form_weight in form_weights
        ]

        tasks = [
            {
                "season": season,
                "time_decay": time_decay,
                "history_years": history_years,
                "training_scope": training_scope,
                "form_match_count": form_match_count,
                "form_weight": form_weight,
                "return_predictions": True
            }
            for (
                form_match_count,
                form_weight
            ) in combinations
        ]

        prediction_sets = self.parallel_runner.run(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if prediction_sets is None:
            return None

        evaluated = evaluate_common_predictions(
            self.engine,
            prediction_sets
        )

        return [
            FormBacktestResult(
                form_match_count=form_match_count,
                form_weight=form_weight,
                **get_result_metrics(result)
            )
            for (
                form_match_count,
                form_weight
            ), result in zip(
                combinations,
                evaluated
            )
        ]
