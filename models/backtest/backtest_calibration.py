from models.backtest.backtest_utils import (
    get_result_metrics,
    is_cancelled
)
from models.analysis.probability_calibration_model import (
    ProbabilityCalibrationModel
)
from models.domains import CalibrationModelBacktestResult


class BacktestCalibration:
    """
        Hanterar backtester av sannolikhetskalibrering.
    """

    CALIBRATION_NONE = "none"
    CALIBRATION_GLOBAL = "global"
    CALIBRATION_LEAGUE = "league"

    def __init__(self, backtest_model):
        self.backtest_model = backtest_model

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
        test_matches = self.backtest_model.soccer_model.get_matches(season_id=season.id)

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
            training_season.id: self.backtest_model.soccer_model.get_matches(
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

        self.backtest_model.analysis_model.clear_analysis_caches()

        test_predictions = self.backtest_model.run(
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

        if (
            test_predictions is None
            or is_cancelled(should_cancel)
        ):
            return None

        # Historiska prognoser.

        predictions_by_season = {}
        progress_offset = len(test_matches)

        for training_season in global_seasons:
            if is_cancelled(should_cancel):
                return None

            self.backtest_model.analysis_model.clear_analysis_caches()

            matches = matches_by_season[training_season.id]

            predictions = self.backtest_model.run(
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

        raw_result = self.backtest_model.engine.evaluate(test_predictions)

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
        seasons = self.backtest_model.soccer_model.get_all_seasons()

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
        result = self.backtest_model.engine.evaluate(calibrated_predictions)

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

