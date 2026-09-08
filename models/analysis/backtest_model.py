from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from queue import Empty, Queue

from database.database import Database
from models.analysis.backtest_engine import BacktestEngine
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

        completed_matches = [
            match
            for match in matches
            if (
                match.home_score is not None
                and match.away_score is not None
                and match.match_date is not None
            )
        ]

        effective_form_weight = form_weight

        if effective_form_weight is None:
            effective_form_weight = (
                self.analysis_model.FORM_WEIGHT
            )

        calculate_form = (
            effective_form_weight != 0.0
        )

        predictions = []

        skipped_matches = (
            len(matches)
            - len(completed_matches)
        )

        if (
            skipped_matches
            and progress_callback is not None
        ):
            progress_callback(
                progress_offset + skipped_matches,
                progress_total
            )

        for index, match in enumerate(
            completed_matches,
            start=1
        ):
            if should_cancel is not None and should_cancel():
                return None

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
                    calculate_form=calculate_form
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
                            progress_offset
                            + skipped_matches
                            + index,
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
                    progress_offset
                    + skipped_matches
                    + index,
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

        execution_combinations = []
        zero_weight_combination = None

        for combination in combinations:
            (
                form_match_count,
                form_weight
            ) = combination

            if form_weight == 0.0:
                if zero_weight_combination is None:
                    zero_weight_combination = combination
                    execution_combinations.append(
                        combination
                    )

                continue

            execution_combinations.append(
                combination
            )

        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        if not matches:
            raise ValueError(
                "Det finns inga matcher att backtesta."
            )

        total_steps = (
            len(matches)
            * len(execution_combinations)
        )

        prediction_sets_by_combination = {}

        for combination_index, (
            form_match_count,
            form_weight
        ) in enumerate(execution_combinations):
            if should_cancel is not None and should_cancel():
                return None

            predictions = self.run(
                season=season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                form_match_count=form_match_count,
                form_weight=form_weight,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=(
                    combination_index
                    * len(matches)
                ),
                progress_total=total_steps,
                return_predictions=True
            )

            if predictions is None:
                return None

            prediction_sets_by_combination[
                (
                    form_match_count,
                    form_weight
                )
            ] = predictions

        prediction_sets = []

        for (
            form_match_count,
            form_weight
        ) in combinations:
            if form_weight == 0.0:
                predictions = (
                    prediction_sets_by_combination[
                        zero_weight_combination
                    ]
                )

            else:
                predictions = (
                    prediction_sets_by_combination[
                        (
                            form_match_count,
                            form_weight
                        )
                    ]
                )

            prediction_sets.append(
                predictions
            )

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
