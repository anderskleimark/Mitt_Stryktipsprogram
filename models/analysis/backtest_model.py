from models.analysis.backtest_engine import BacktestEngine
from mvc import Model
from models.domains import (
    BacktestPrediction,
    TimeDecayBacktestResult
)


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
        start_date,
        end_date,
        time_decay=None,
        should_cancel=None,
        matches=None,
        progress_callback=None,
        progress_offset=0,
        progress_total=None
    ):
        """
            Backtestar modellen på färdigspelade
            matcher inom angivet datumintervall.

            Körningen kan avbrytas via
            should_cancel.

            Om progress_callback anges rapporteras
            hur långt körningen har kommit.
        """
        if matches is None:
            matches = (
                self.soccer_model
                .get_competition_matches_between_dates(
                    season.competition.id,
                    start_date,
                    end_date
                )
            )

        predictions = []

        for index, match in enumerate(
            matches,
            start=1
        ):
            if (
                should_cancel is not None
                and should_cancel()
            ):
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
                analysis = (
                    self.analysis_model
                    .analyze_match(
                        season=match.season,
                        home_team=match.home_team,
                        away_team=match.away_team,
                        reference_date=match.match_date,
                        time_decay=time_decay
                    )
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

            if (
                should_cancel is not None
                and should_cancel()
            ):
                return None

            prediction = (
                self._create_prediction(
                    match,
                    analysis
                )
            )

            predictions.append(
                prediction
            )

            if progress_callback is not None:
                progress_callback(
                    progress_offset + index,
                    progress_total
                )

        if (
            should_cancel is not None
            and should_cancel()
        ):
            return None

        if not predictions:
            raise ValueError(
                "Det finns inga prognoser att utvärdera."
            )

        return self.engine.evaluate(
            predictions
        )

    def _create_prediction(
        self,
        match,
        analysis
    ):
        """
            Skapar en historisk prognos från
            matchanalysen.
        """
        match_result = (
            analysis.odds_analysis.match_result
        )

        return BacktestPrediction(
            match_date=match.match_date,

            home_team=match.home_team,
            away_team=match.away_team,

            probability_1=(
                match_result["1"].probability
            ),

            probability_x=(
                match_result["X"].probability
            ),

            probability_2=(
                match_result["2"].probability
            ),

            actual_result=match.result_1x2
        )

    def run_time_decay_comparison(
        self,
        *,
        season,
        start_date,
        end_date,
        time_decay_values,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Kör samma backtest med flera
            time-decay-värden.

            Körningen kan avbrytas via
            should_cancel.

            Om progress_callback anges rapporteras
            totalt antal genomförda steg.
        """
        matches = (
            self.soccer_model
            .get_competition_matches_between_dates(
                season.competition.id,
                start_date,
                end_date
            )
        )

        results = []

        matches_per_run = len(
            matches
        )

        total_steps = (
            len(time_decay_values)
            * matches_per_run
        )

        for index, time_decay in enumerate(
            time_decay_values
        ):
            if (
                should_cancel is not None
                and should_cancel()
            ):
                return None

            progress_offset = (
                index
                * matches_per_run
            )

            result = self.run(
                season=season,
                start_date=start_date,
                end_date=end_date,
                time_decay=time_decay,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=progress_offset,
                progress_total=total_steps
            )

            if result is None:
                return None

            results.append(
                TimeDecayBacktestResult(
                    time_decay=time_decay,

                    matches_tested=(
                        result.matches_tested
                    ),

                    brier_score=(
                        result.brier_score
                    ),

                    log_loss=(
                        result.log_loss
                    ),

                    accuracy=(
                        result.accuracy
                    ),

                    uniform_brier_score=(
                        result.uniform_brier_score
                    ),

                    uniform_log_loss=(
                        result.uniform_log_loss
                    ),

                    historical_brier_score=(
                        result.historical_brier_score
                    ),

                    historical_log_loss=(
                        result.historical_log_loss
                    ),

                    calibration_bins=(
                        result.calibration_bins
                    )
                )
            )

        return results
