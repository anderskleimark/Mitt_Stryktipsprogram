from models.analysis.backtest_engine import BacktestEngine
from models.domains import (BacktestPrediction, HistoryYearsBacktestResult,
                            TimeDecayBacktestResult,
                            TrainingScopeBacktestResult)
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

    def run(
        self,
        *,
        season,
        time_decay=None,
        history_years=None,
        training_scope=None,
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
                    training_scope=training_scope
                )

            except ValueError as error:
                message = str(error)

                if message in (
                    "Hemmalaget saknas i Dixon-Coles-modellen.",
                    "Bortalaget saknas i Dixon-Coles-modellen.",
                    "Det finns inga färdigspelade matcher för Dixon-Coles-modellen.",
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

            predictions.append(prediction)

            if progress_callback is not None:
                progress_callback(
                    progress_offset + index,
                    progress_total
                )

        if should_cancel is not None and should_cancel():
            return None

        if not predictions:
            raise ValueError("Det finns inga prognoser att utvärdera.")

        if return_predictions:
            return predictions

        return self.engine.evaluate(predictions)

    def _create_prediction(
        self,
        match,
        analysis
    ):
        """
            Skapar en historisk prognos från
            matchanalysen.
        """
        match_result = analysis.odds_analysis.match_result

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
                self._prediction_key(prediction)
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
            if self._prediction_key(prediction) in common_keys
        ]

    def run_time_decay_comparison(
        self,
        *,
        season,
        time_decay_values,
        history_years,
        training_scope,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör samma backtest med flera
            time-decay-värden.

            Historiklängd och träningsdata hålls
            konstanta under hela jämförelsen.

            Körningen kan avbrytas via
            should_cancel.

            Om progress_callback anges rapporteras
            totalt antal genomförda steg.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        results = []
        matches_per_run = len(matches)
        total_steps = len(time_decay_values) * matches_per_run

        for index, time_decay in enumerate(time_decay_values):
            if should_cancel is not None and should_cancel():
                return None

            result = self.run(
                season=season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=index * matches_per_run,
                progress_total=total_steps
            )

            if result is None:
                return None

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

    def run_history_years_comparison(
        self,
        *,
        season,
        history_years_values,
        time_decay,
        training_scope,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör samma backtest med flera
            olika historiklängder.

            Time decay och träningsdata hålls
            konstanta under hela jämförelsen.

            Endast matcher som kan prognostiseras
            med samtliga historiklängder utvärderas.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        prediction_sets = []
        matches_per_run = len(matches)
        total_steps = len(history_years_values) * matches_per_run

        for index, history_years in enumerate(history_years_values):
            if should_cancel is not None and should_cancel():
                return None

            predictions = self.run(
                season=season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=index * matches_per_run,
                progress_total=total_steps,
                return_predictions=True
            )

            if predictions is None:
                return None

            prediction_sets.append(predictions)

        if should_cancel is not None and should_cancel():
            return None

        common_keys = self._get_common_prediction_keys(
            prediction_sets
        )

        if not common_keys:
            raise ValueError(
                "Det finns inga gemensamma prognoser att utvärdera."
            )

        results = []

        for history_years, predictions in zip(
            history_years_values,
            prediction_sets
        ):
            common_predictions = self._filter_predictions(
                predictions,
                common_keys
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

    def run_training_scope_comparison(
        self,
        *,
        season,
        training_scopes,
        time_decay,
        history_years,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör samma backtest med flera
            omfattningar av träningsdata.

            Time decay och historiklängd hålls
            konstanta under hela jämförelsen.
        """
        matches = self.soccer_model.get_matches(
            season_id=season.id
        )

        results = []
        matches_per_run = len(matches)
        total_steps = len(training_scopes) * matches_per_run

        for index, training_scope in enumerate(training_scopes):
            if should_cancel is not None and should_cancel():
                return None

            result = self.run(
                season=season,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=index * matches_per_run,
                progress_total=total_steps
            )

            if result is None:
                return None

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
