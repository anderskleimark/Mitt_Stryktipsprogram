import math
import statistics
from types import SimpleNamespace

import numpy as np
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from queue import Empty, Queue

from database.database import Database
from models.analysis.backtest_engine import BacktestEngine
from models.analysis.dixon_coles_model import DixonColesModel
from models.analysis_model import AnalysisModel
from models.domains import (BacktestPrediction, FormBacktestResult,
                            HistoryYearsBacktestResult,
                            TimeDecayBacktestResult,
                            TrainingScopeBacktestResult)
from models.soccer_model import SoccerModel
from mvc import Model


class BacktestModel(Model):
    """
        Genomför historiska backtester av
        matchanalysmodellen.
    """

    def __init__(
        self,
        *,
        soccer_model,
        analysis_model
    ):
        self.soccer_model = soccer_model
        self.analysis_model = analysis_model

        self.engine = BacktestEngine()

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
        should_cancel=None,
        matches=None,
        progress_callback=None,
        progress_offset=0,
        progress_total=None,
        return_predictions=False
    ):
        """
            Backtestar modellen på färdigspelade
            matcher i den valda säsongen.

            Körningen kan avbrytas via
            should_cancel.

            Om progress_callback anges rapporteras
            hur långt körningen har kommit.

            Om return_predictions är True returneras
            prognoserna utan att utvärderas.
        """
        if matches is None:
            matches = self.soccer_model.get_matches(
                season_id=season.id
            )

        if progress_total is None:
            progress_total = len(matches)

        effective_form_weight = form_weight

        if effective_form_weight is None:
            effective_form_weight = (
                self.analysis_model.FORM_WEIGHT
            )

        calculate_form = (
            effective_form_weight != 0.0
        )

        effective_h2h_weight = h2h_weight

        if effective_h2h_weight is None:
            effective_h2h_weight = (
                self.analysis_model.H2H_WEIGHT
            )

        calculate_h2h = (
            effective_h2h_weight != 0.0
        )

        predictions = []

        for index, match in enumerate(matches, start=1):
            if should_cancel is not None and should_cancel():
                return None

            if (
                match.home_score is None
                or match.away_score is None
                or match.match_date is None
            ):
                if progress_callback is not None:
                    progress_callback(
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
                    time_decay=time_decay,
                    history_years=history_years,
                    training_scope=training_scope,
                    form_match_count=form_match_count,
                    form_weight=form_weight,
                    calculate_form=calculate_form,
                    h2h_match_count=h2h_match_count,
                    h2h_weight=h2h_weight,
                    calculate_h2h=calculate_h2h,
                    rho_mode=rho_mode
                )

            except ValueError as error:
                message = str(error)

                if message in (
                    "Hemmalaget saknas i Dixon-Coles-modellen.",
                    "Bortalaget saknas i Dixon-Coles-modellen.",
                    "Det finns inga färdigspelade matcher för "
                    "Dixon-Coles-modellen.",
                    "För få lag för Dixon-Coles-modellen.",
                    "Referenstävlingen saknas i modellens matcher."
                ):
                    if progress_callback is not None:
                        progress_callback(
                            progress_offset + index,
                            progress_total
                        )

                    continue

                raise

            if should_cancel is not None and should_cancel():
                return None

            prediction = self._create_prediction(
                match,
                analysis
            )

            predictions.append(
                prediction
            )

            if progress_callback is not None:
                progress_callback(
                    progress_offset + index,
                    progress_total
                )

        if should_cancel is not None and should_cancel():
            return None

        if not predictions:
            raise ValueError(
                "Det finns inga prognoser att utvärdera."
            )

        if return_predictions:
            return predictions

        return self.engine.evaluate(
            predictions
        )

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
            Jämför fritt skattad rho med rho låst till 0.0.

            Båda modellerna utvärderas på exakt samma matcher.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        total_steps = len(matches) * 2

        self.analysis_model.clear_analysis_caches()

        estimated_predictions = self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=DixonColesModel.RHO_MODE_ESTIMATED,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=0,
            progress_total=total_steps,
            return_predictions=True
        )

        if estimated_predictions is None:
            return None

        self.analysis_model.clear_analysis_caches()

        zero_predictions = self.run(
            season=season,
            time_decay=time_decay,
            history_years=history_years,
            training_scope=training_scope,
            form_weight=0.0,
            rho_mode=DixonColesModel.RHO_MODE_FIXED,
            should_cancel=should_cancel,
            matches=matches,
            progress_callback=progress_callback,
            progress_offset=len(matches),
            progress_total=total_steps,
            return_predictions=True
        )

        if zero_predictions is None:
            return None

        common_keys = self._get_common_prediction_keys(
            [
                estimated_predictions,
                zero_predictions
            ]
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma prognoser för rho-jämförelsen."
            )

        estimated_result = self.engine.evaluate(
            self._filter_predictions(
                estimated_predictions,
                common_keys
            )
        )

        zero_result = self.engine.evaluate(
            self._filter_predictions(
                zero_predictions,
                common_keys
            )
        )

        return [
            self._create_rho_comparison_result(
                "Skattad",
                estimated_result
            ),
            self._create_rho_comparison_result(
                "0.0",
                zero_result
            )
        ]

    @staticmethod
    def _create_rho_comparison_result(label, result):
        """
            Skapar ett tabellkompatibelt resultat
            för rho-jämförelsen.
        """
        return SimpleNamespace(
            rho_label=label,
            matches_tested=result.matches_tested,
            brier_score=result.brier_score,
            log_loss=result.log_loss,
            accuracy=result.accuracy,
            uniform_brier_score=result.uniform_brier_score,
            uniform_log_loss=result.uniform_log_loss,
            historical_brier_score=result.historical_brier_score,
            historical_log_loss=result.historical_log_loss,
            calibration_bins=result.calibration_bins
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
            Kör ett vanligt backtest och sammanställer
            de rho-värden som skattas av Dixon-Coles-modellen.
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
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date is not None
            )
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

        diagnostics = self.analysis_model.get_rho_diagnostics()

        if not diagnostics:
            raise ValueError(
                "Inga rho-värden samlades in under backtestet."
            )

        rho_values = [
            item["rho"]
            for item in diagnostics
        ]

        reference_dates = [
            item["reference_date"]
            for item in diagnostics
        ]

        unique_reference_dates = set(reference_dates)

        missing_reference_dates = sorted(
            match_dates - unique_reference_dates
        )

        extra_reference_dates = sorted(
            unique_reference_dates - match_dates
        )

        model = self.analysis_model.engine.dixon_coles_model
        lower_bound = model.RHO_MIN
        upper_bound = model.RHO_MAX
        bound_tolerance = 0.001

        lower_bound_count = sum(
            math.isclose(
                rho,
                lower_bound,
                rel_tol=0.0,
                abs_tol=bound_tolerance
            )
            for rho in rho_values
        )

        upper_bound_count = sum(
            math.isclose(
                rho,
                upper_bound,
                rel_tol=0.0,
                abs_tol=bound_tolerance
            )
            for rho in rho_values
        )

        count = len(rho_values)

        return {
            "backtest_result": result,
            "match_count": len(completed_matches),
            "match_date_count": len(match_dates),
            "count": count,
            "reference_date_count": len(unique_reference_dates),
            "duplicate_reference_date_count": (
                count - len(unique_reference_dates)
            ),
            "missing_reference_date_count": len(missing_reference_dates),
            "extra_reference_date_count": len(extra_reference_dates),
            "missing_reference_dates": missing_reference_dates,
            "extra_reference_dates": extra_reference_dates,
            "minimum": min(rho_values),
            "percentile_05": float(np.percentile(rho_values, 5)),
            "mean": statistics.mean(rho_values),
            "median": statistics.median(rho_values),
            "percentile_95": float(np.percentile(rho_values, 95)),
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
    # Parallell körning
    # --------------------------------------------------

    def _run_isolated(
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
        progress_callback=None,
        return_predictions=False
    ):
        """
            Kör ett backtest med en egen
            databasanslutning och egna modeller.

            Metoden är avsedd att köras i
            en separat executor-tråd.
        """
        database = None

        try:
            if should_cancel is not None and should_cancel():
                return None

            database = Database(
                initialize=False
            )

            soccer_model = SoccerModel(
                database
            )

            analysis_model = AnalysisModel(
                database,
                soccer_model
            )

            backtest_model = BacktestModel(
                soccer_model=soccer_model,
                analysis_model=analysis_model
            )

            return backtest_model.run(
                season=season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                form_match_count=form_match_count,
                form_weight=form_weight,
                h2h_match_count=h2h_match_count,
                h2h_weight=h2h_weight,
                rho_mode=rho_mode,
                should_cancel=should_cancel,
                progress_callback=progress_callback,
                return_predictions=return_predictions
            )

        finally:
            if database is not None:
                database.close()

    def _run_parallel(
        self,
        *,
        tasks,
        should_cancel=None,
        progress_callback=None,
        max_workers=None
    ):
        """
            Kör flera oberoende backtest parallellt.

            Varje körning använder en egen
            databasanslutning och egna modeller.

            Progress från executor-trådarna läggs
            i en kö och rapporteras sedan från
            den koordinerande worker-tråden.

            Resultaten returneras i samma ordning
            som uppgifterna anges.
        """
        if not tasks:
            return []

        results = [
            None
            for _ in tasks
        ]

        matches = self.soccer_model.get_matches(
            season_id=tasks[0]["season"].id
        )

        matches_per_run = len(matches)

        if matches_per_run <= 0:
            raise ValueError(
                "Det finns inga matcher att backtesta."
            )

        total_steps = (
            matches_per_run
            * len(tasks)
        )

        task_progress = [
            0
            for _ in tasks
        ]

        progress_queue = Queue()

        executor = ThreadPoolExecutor(
            max_workers=max_workers
        )

        futures = {}

        try:
            for index, task in enumerate(tasks):
                if should_cancel is not None and should_cancel():
                    break

                def report_task_progress(
                    completed,
                    total,
                    *,
                    task_index=index
                ):
                    progress_queue.put(
                        (
                            task_index,
                            completed
                        )
                    )

                future = executor.submit(
                    self._run_isolated,
                    should_cancel=should_cancel,
                    progress_callback=report_task_progress,
                    **task
                )

                futures[future] = index

            pending = set(
                futures
            )

            while pending:
                if should_cancel is not None and should_cancel():
                    for future in pending:
                        future.cancel()

                    return None

                self._process_parallel_progress(
                    progress_queue=progress_queue,
                    task_progress=task_progress,
                    matches_per_run=matches_per_run,
                    total_steps=total_steps,
                    progress_callback=progress_callback
                )

                done, pending = wait(
                    pending,
                    timeout=0.1,
                    return_when=FIRST_COMPLETED
                )

                for future in done:
                    index = futures[future]

                    result = future.result()

                    if result is None:
                        for pending_future in pending:
                            pending_future.cancel()

                        return None

                    results[index] = result

                    task_progress[index] = (
                        matches_per_run
                    )

                    if progress_callback is not None:
                        progress_callback(
                            sum(task_progress),
                            total_steps
                        )

            self._process_parallel_progress(
                progress_queue=progress_queue,
                task_progress=task_progress,
                matches_per_run=matches_per_run,
                total_steps=total_steps,
                progress_callback=progress_callback
            )

        finally:
            executor.shutdown(
                wait=True,
                cancel_futures=True
            )

        if should_cancel is not None and should_cancel():
            return None

        return results

    def _process_parallel_progress(
        self,
        *,
        progress_queue,
        task_progress,
        matches_per_run,
        total_steps,
        progress_callback
    ):
        """
            Hämtar progress från executor-trådarna
            och rapporterar sammanlagd progress.
        """
        progress_changed = False

        while True:
            try:
                (
                    task_index,
                    completed
                ) = progress_queue.get_nowait()

            except Empty:
                break

            completed = min(
                max(completed, 0),
                matches_per_run
            )

            if completed > task_progress[task_index]:
                task_progress[task_index] = completed
                progress_changed = True

        if (
            progress_changed
            and progress_callback is not None
        ):
            progress_callback(
                sum(task_progress),
                total_steps
            )

    # --------------------------------------------------
    # Prognoser
    # --------------------------------------------------

    def _create_prediction(
        self,
        match,
        analysis
    ):
        """
            Skapar en historisk prognos
            från matchanalysen.
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
            actual_result=match.result_1x2
        )

    def _prediction_key(
        self,
        prediction
    ):
        """
            Skapar en unik nyckel för
            en historisk prognos.
        """
        return (
            prediction.match_date,
            prediction.home_team.id,
            prediction.away_team.id
        )

    def _get_common_prediction_keys(
        self,
        prediction_sets
    ):
        """
            Hämtar de matcher som finns med
            i samtliga prognosuppsättningar.
        """
        common_keys = None

        for predictions in prediction_sets:
            prediction_keys = {
                self._prediction_key(
                    prediction
                )
                for prediction in predictions
            }

            if common_keys is None:
                common_keys = prediction_keys

            else:
                common_keys &= prediction_keys

        if common_keys is None:
            return set()

        return common_keys

    def _filter_predictions(
        self,
        predictions,
        common_keys
    ):
        """
            Filtrerar prognoser till de matcher
            som finns i samtliga jämförelser.
        """
        return [
            prediction
            for prediction in predictions
            if self._prediction_key(
                prediction
            ) in common_keys
        ]

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
            Kör samma backtest med flera
            time-decay-värden.

            Historiklängd, träningsdata och
            formparametrar hålls konstanta.
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

        backtest_results = self._run_parallel(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if backtest_results is None:
            return None

        results = []

        for time_decay, result in zip(
            time_decay_values,
            backtest_results
        ):
            results.append(
                TimeDecayBacktestResult(
                    time_decay=time_decay,
                    matches_tested=result.matches_tested,
                    brier_score=result.brier_score,
                    log_loss=result.log_loss,
                    accuracy=result.accuracy,
                    uniform_brier_score=result.uniform_brier_score,
                    uniform_log_loss=result.uniform_log_loss,
                    historical_brier_score=result.historical_brier_score,
                    historical_log_loss=result.historical_log_loss,
                    calibration_bins=result.calibration_bins
                )
            )

        return results

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
            Kör samma backtest med flera
            olika historiklängder.

            Time decay, träningsdata och
            formparametrar hålls konstanta.

            Endast matcher som kan prognostiseras
            med samtliga historiklängder utvärderas.
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

        prediction_sets = self._run_parallel(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if prediction_sets is None:
            return None

        common_keys = self._get_common_prediction_keys(
            prediction_sets
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma "
                "prognoser att utvärdera."
            )

        results = []

        for history_years, predictions in zip(
            history_years_values,
            prediction_sets
        ):
            common_predictions = (
                self._filter_predictions(
                    predictions,
                    common_keys
                )
            )

            result = self.engine.evaluate(
                common_predictions
            )

            results.append(
                HistoryYearsBacktestResult(
                    history_years=history_years,
                    matches_tested=result.matches_tested,
                    brier_score=result.brier_score,
                    log_loss=result.log_loss,
                    accuracy=result.accuracy,
                    uniform_brier_score=result.uniform_brier_score,
                    uniform_log_loss=result.uniform_log_loss,
                    historical_brier_score=result.historical_brier_score,
                    historical_log_loss=result.historical_log_loss,
                    calibration_bins=result.calibration_bins
                )
            )

        return results

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
            Kör samma backtest med flera
            omfattningar av träningsdata.

            Time decay, historiklängd och
            formparametrar hålls konstanta.
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

        backtest_results = self._run_parallel(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if backtest_results is None:
            return None

        results = []

        for training_scope, result in zip(
            training_scopes,
            backtest_results
        ):
            results.append(
                TrainingScopeBacktestResult(
                    training_scope=training_scope,
                    matches_tested=result.matches_tested,
                    brier_score=result.brier_score,
                    log_loss=result.log_loss,
                    accuracy=result.accuracy,
                    uniform_brier_score=result.uniform_brier_score,
                    uniform_log_loss=result.uniform_log_loss,
                    historical_brier_score=result.historical_brier_score,
                    historical_log_loss=result.historical_log_loss,
                    calibration_bins=result.calibration_bins
                )
            )

        return results

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
            Jämför olika vikter för inbördes möten.

            Antalet H2H-matcher hålls konstant och
            endast gemensamma prognoser utvärderas.
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
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date is not None
            )
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
            len(completed_matches) - len(eligible_matches)
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
                "form_weight": 0.0,
                "h2h_match_count": h2h_match_count,
                "h2h_weight": h2h_weight,
                "return_predictions": True
            }
            for h2h_weight in h2h_weights
        ]

        prediction_sets = []
        total_steps = len(eligible_matches) * len(tasks)

        for task_index, task in enumerate(tasks):
            if should_cancel is not None and should_cancel():
                return None

            self.analysis_model.clear_analysis_caches()

            predictions = self.run(
                **task,
                should_cancel=should_cancel,
                matches=eligible_matches,
                progress_callback=progress_callback,
                progress_offset=task_index * len(eligible_matches),
                progress_total=total_steps
            )

            if predictions is None:
                return None

            prediction_sets.append(predictions)

        if prediction_sets is None:
            return None

        common_keys = self._get_common_prediction_keys(
            prediction_sets
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma prognoser "
                "för H2H-jämförelsen."
            )

        results = []

        for h2h_weight, predictions in zip(
            h2h_weights,
            prediction_sets
        ):
            result = self.engine.evaluate(
                self._filter_predictions(
                    predictions,
                    common_keys
                )
            )

            results.append(
                SimpleNamespace(
                    h2h_weight=h2h_weight,
                    matches_tested=result.matches_tested,
                    h2h_eligible_matches=len(eligible_matches),
                    h2h_excluded_matches=excluded_match_count,
                    h2h_required_matches=h2h_match_count,
                    brier_score=result.brier_score,
                    log_loss=result.log_loss,
                    accuracy=result.accuracy,
                    uniform_brier_score=result.uniform_brier_score,
                    uniform_log_loss=result.uniform_log_loss,
                    historical_brier_score=result.historical_brier_score,
                    historical_log_loss=result.historical_log_loss,
                    calibration_bins=result.calibration_bins
                )
            )

        return results

    def _has_required_h2h_history(
        self,
        match,
        required_match_count
    ):
        """
            Kontrollerar att matchen har minst angivet
            antal färdigspelade H2H-matcher före matchdatumet.
        """
        h2h_matches = self.soccer_model.get_head_to_head_matches(
            home_team_id=match.home_team.id,
            away_team_id=match.away_team.id,
            reference_date=match.match_date
        )

        completed_h2h_matches = [
            h2h_match
            for h2h_match in h2h_matches
            if (
                h2h_match.home_score is not None
                and h2h_match.away_score is not None
                and h2h_match.match_date is not None
                and h2h_match.match_date < match.match_date
            )
        ]

        return len(completed_h2h_matches) >= required_match_count

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

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
            Jämför olika kombinationer av antal
            formmatcher och formvikt.

            Time decay, historiklängd och omfattning
            av träningsdata hålls konstanta.

            Endast matcher som kan prognostiseras
            med samtliga kombinationer utvärderas.
        """
        if not form_match_counts:
            raise ValueError(
                "Det finns inga antal formmatcher "
                "att jämföra."
            )

        if not form_weights:
            raise ValueError(
                "Det finns inga formvikter "
                "att jämföra."
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

        prediction_sets = self._run_parallel(
            tasks=tasks,
            should_cancel=should_cancel,
            progress_callback=progress_callback,
            max_workers=max_workers
        )

        if prediction_sets is None:
            return None

        common_keys = self._get_common_prediction_keys(
            prediction_sets
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma "
                "prognoser att utvärdera."
            )

        results = []

        for (
            form_match_count,
            form_weight
        ), predictions in zip(
            combinations,
            prediction_sets
        ):
            common_predictions = (
                self._filter_predictions(
                    predictions,
                    common_keys
                )
            )

            result = self.engine.evaluate(
                common_predictions
            )

            results.append(
                FormBacktestResult(
                    form_match_count=form_match_count,
                    form_weight=form_weight,
                    matches_tested=result.matches_tested,
                    brier_score=result.brier_score,
                    log_loss=result.log_loss,
                    accuracy=result.accuracy,
                    uniform_brier_score=result.uniform_brier_score,
                    uniform_log_loss=result.uniform_log_loss,
                    historical_brier_score=result.historical_brier_score,
                    historical_log_loss=result.historical_log_loss,
                    calibration_bins=result.calibration_bins
                )
            )

        return results
