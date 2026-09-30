from models.backtest.backtest_utils import (
    get_result_metrics,
    is_cancelled
)
from models.analysis.probability_calibration_model import (
    ProbabilityCalibrationModel
)
from models.domains import (
    CalibrationModelBacktestResult,
    FinalValidationBacktestResult,
    MinCalibrationMatchesBacktestResult
)


class BacktestCalibration:
    """
        Hanterar backtester av sannolikhetskalibrering.
    """

    CALIBRATION_NONE = "none"
    CALIBRATION_GLOBAL = "global"
    CALIBRATION_LEAGUE = "league"

    def __init__(self, backtest_model):
        self.backtest_model = backtest_model


    def run_final_validation(
        self,
        *,
        season,
        time_decay,
        history_years,
        training_scope,
        calibration_years,
        min_calibration_matches,
        form_match_count,
        form_weight,
        h2h_match_count,
        h2h_weight,
        should_cancel=None,
        progress_callback=None
    ):
        """
        Slutvaliderar den låsta produktionsmodellen över alla
        testsäsonger i vald liga t.o.m. vald avslutad säsong.

        För varje testsäsong skattas beta från de senaste
        calibration_years säsongsåren i samma land. Kalibrering
        används bara när träningsmängden når miniminivån.
        """
        all_seasons = self.backtest_model.soccer_model.get_all_seasons()
        test_seasons = self._get_unique_seasons([
            candidate for candidate in all_seasons
            if (candidate.competition.id == season.competition.id
                and candidate.start_year <= season.start_year)
        ])
        if not test_seasons:
            raise ValueError("Det finns inga testsäsonger att slutvalidera.")

        calibration_seasons_by_test = {}
        for test_season in test_seasons:
            previous = [
                candidate for candidate in all_seasons
                if (self._is_previous_season(candidate, test_season)
                    and candidate.competition.country.id
                    == test_season.competition.country.id)
            ]
            start_years = set(sorted(
                {candidate.start_year for candidate in previous},
                reverse=True
            )[:calibration_years])
            calibration_seasons_by_test[test_season.id] = self._get_unique_seasons([
                candidate for candidate in previous
                if candidate.start_year in start_years
            ])

        required = {item.id: item for item in test_seasons}
        for seasons in calibration_seasons_by_test.values():
            for item in seasons:
                required[item.id] = item
        required_seasons = self._get_unique_seasons(list(required.values()))
        matches_by_season = {
            item.id: self.backtest_model.soccer_model.get_matches(season_id=item.id)
            for item in required_seasons
        }
        total_steps = sum(len(items) for items in matches_by_season.values())
        if total_steps <= 0:
            raise ValueError("Det finns inga matcher att slutvalidera.")

        predictions_by_season = {}
        progress_offset = 0
        for item in required_seasons:
            if is_cancelled(should_cancel):
                return None
            self.backtest_model.analysis_model.clear_analysis_caches()
            matches = matches_by_season[item.id]
            predictions = self.backtest_model.run(
                season=item,
                time_decay=time_decay,
                history_years=history_years,
                training_scope=training_scope,
                form_match_count=form_match_count,
                form_weight=form_weight,
                h2h_match_count=h2h_match_count,
                h2h_weight=h2h_weight,
                should_cancel=should_cancel,
                matches=matches,
                progress_callback=progress_callback,
                progress_offset=progress_offset,
                progress_total=total_steps,
                return_predictions=True
            )
            if predictions is None:
                return None
            predictions_by_season[item.id] = predictions
            progress_offset += len(matches)

        aggregate = []
        calibrated_matches = 0
        training_counts = []
        used_test_seasons = 0

        for test_season in test_seasons:
            if is_cancelled(should_cancel):
                return None
            test_predictions = predictions_by_season.get(test_season.id, [])
            if not test_predictions:
                continue
            used_test_seasons += 1
            training_predictions = self._combine_season_predictions(
                calibration_seasons_by_test[test_season.id],
                predictions_by_season
            )
            training_count = len(training_predictions)
            training_counts.append(training_count)
            if training_count >= min_calibration_matches and training_predictions:
                calibrator = ProbabilityCalibrationModel()
                calibrator.fit(training_predictions)
                aggregate.extend(calibrator.transform(test_predictions))
                calibrated_matches += len(test_predictions)
            else:
                aggregate.extend(test_predictions)

        if not aggregate:
            raise ValueError("Det finns inga testprognoser att slutvalidera.")

        evaluation = self.backtest_model.engine.evaluate(aggregate)
        return [FinalValidationBacktestResult(
            test_seasons=used_test_seasons,
            end_season_name=season.display_name,
            calibrated_matches=calibrated_matches,
            min_training_matches=min(training_counts) if training_counts else 0,
            max_training_matches=max(training_counts) if training_counts else 0,
            **get_result_metrics(evaluation)
        )]

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

    def run_min_calibration_matches_comparison(
        self,
        *,
        season,
        min_calibration_matches_values,
        time_decay,
        history_years,
        training_scope,
        calibration_years=3,
        form_match_count=None,
        form_weight=None,
        should_cancel=None,
        progress_callback=None
    ):
        """
            Jämför minsta antal kalibreringsmatcher över flera
            testsäsonger i den valda ligan.

            För varje testsäsong används samma globala
            kalibreringsunderlag som i produktion:
            de senaste calibration_years säsongsåren från
            samma land, strikt före testsäsongen.

            Råprognoser för varje säsong beräknas bara en gång
            och återanvänds för samtliga miniminivåer.
        """
        if not min_calibration_matches_values:
            raise ValueError(
                "Inga miniminivåer för kalibreringsmatcher har angetts."
            )

        all_seasons = self.backtest_model.soccer_model.get_all_seasons()

        test_seasons = self._get_unique_seasons([
            candidate
            for candidate in all_seasons
            if (
                candidate.competition.id == season.competition.id
                and candidate.start_year <= season.start_year
            )
        ])

        if not test_seasons:
            raise ValueError(
                "Det finns inga testsäsonger i den valda ligan."
            )

        # Produktionsmotsvarande kalibreringssäsonger per testsäsong.
        calibration_seasons_by_test = {}

        for test_season in test_seasons:
            previous_country_seasons = [
                candidate
                for candidate in all_seasons
                if (
                    self._is_previous_season(candidate, test_season)
                    and candidate.competition.country.id
                    == test_season.competition.country.id
                )
            ]

            start_years = sorted(
                {
                    candidate.start_year
                    for candidate in previous_country_seasons
                },
                reverse=True
            )[:calibration_years]
            start_years = set(start_years)

            calibration_seasons_by_test[test_season.id] = (
                self._get_unique_seasons([
                    candidate
                    for candidate in previous_country_seasons
                    if candidate.start_year in start_years
                ])
            )

        # Alla säsonger vars råprognoser behövs. Samma säsong
        # kan vara testsäsong i en körning och kalibreringssäsong
        # i en annan, men beräknas ändå bara en gång.
        required_seasons = {
            test_season.id: test_season
            for test_season in test_seasons
        }

        for calibration_seasons in calibration_seasons_by_test.values():
            for calibration_season in calibration_seasons:
                required_seasons[calibration_season.id] = calibration_season

        required_seasons = self._get_unique_seasons(
            list(required_seasons.values())
        )

        matches_by_season = {
            required_season.id:
                self.backtest_model.soccer_model.get_matches(
                    season_id=required_season.id
                )
            for required_season in required_seasons
        }

        total_steps = sum(
            len(matches)
            for matches in matches_by_season.values()
        )

        if total_steps <= 0:
            raise ValueError(
                "Det finns inga matcher att använda "
                "i kalibreringsjämförelsen."
            )

        # Skapa alla råa OOS-prognoser en gång.
        predictions_by_season = {}
        progress_offset = 0

        for required_season in required_seasons:
            if is_cancelled(should_cancel):
                return None

            self.backtest_model.analysis_model.clear_analysis_caches()

            matches = matches_by_season[required_season.id]

            predictions = self.backtest_model.run(
                season=required_season,
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

            predictions_by_season[required_season.id] = predictions
            progress_offset += len(matches)

        if is_cancelled(should_cancel):
            return None

        aggregate_predictions = {
            minimum: []
            for minimum in min_calibration_matches_values
        }
        calibrated_matches = {
            minimum: 0
            for minimum in min_calibration_matches_values
        }

        training_match_counts = []
        used_test_seasons = 0

        # Varje testsäsong får sin egen beta, skattad enbart
        # från data som var historisk vid den säsongens start.
        for test_season in test_seasons:
            if is_cancelled(should_cancel):
                return None

            test_predictions = predictions_by_season.get(
                test_season.id,
                []
            )

            if not test_predictions:
                continue

            used_test_seasons += 1

            calibration_seasons = calibration_seasons_by_test[
                test_season.id
            ]
            training_predictions = self._combine_season_predictions(
                calibration_seasons,
                predictions_by_season
            )
            training_count = len(training_predictions)
            training_match_counts.append(training_count)

            # Tillfällig diagnostik:
            # visar den verkliga brytpunkten för varje testsäsong.
            print(
                "[MIN_CALIBRATION_MATCHES] "
                f"{test_season.start_year}/{test_season.end_year}: "
                f"{training_count} kalibreringsmatcher"
            )

            calibrated_predictions = None

            if training_predictions:
                calibrator = ProbabilityCalibrationModel()
                calibrator.fit(training_predictions)
                calibrated_predictions = calibrator.transform(
                    test_predictions
                )

            for minimum in min_calibration_matches_values:
                use_calibration = (
                    calibrated_predictions is not None
                    and training_count >= minimum
                )

                if use_calibration:
                    aggregate_predictions[minimum].extend(
                        calibrated_predictions
                    )
                    calibrated_matches[minimum] += len(test_predictions)
                else:
                    aggregate_predictions[minimum].extend(
                        test_predictions
                    )

        if used_test_seasons == 0:
            raise ValueError(
                "Det finns inga testprognoser att utvärdera."
            )

        results = []

        for minimum in min_calibration_matches_values:
            if is_cancelled(should_cancel):
                return None

            predictions = aggregate_predictions[minimum]

            if not predictions:
                continue

            evaluation = self.backtest_model.engine.evaluate(predictions)

            results.append(
                MinCalibrationMatchesBacktestResult(
                    min_calibration_matches=minimum,
                    test_seasons=used_test_seasons,
                    calibrated_matches=calibrated_matches[minimum],
                    min_training_matches=min(training_match_counts),
                    max_training_matches=max(training_match_counts),
                    **get_result_metrics(evaluation)
                )
            )

        return results

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

