
from models.backtest.backtest_engine import BacktestEngine
from models.backtest.backtest_calibration import BacktestCalibration
from models.backtest.backtest_diagnostics import BacktestDiagnostics
from models.backtest.backtest_parameter_comparison import (
    BacktestParameterComparison
)
from models.backtest.backtest_utils import (
    is_cancelled,
    is_completed_match,
    report_progress
)
from models.analysis.dixon_coles_model import DixonColesModel
from models.domains import BacktestPrediction
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
        self.calibration = BacktestCalibration(self)
        self.diagnostics = BacktestDiagnostics(self)
        self.parameter_comparison = BacktestParameterComparison(self)

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
                    home_advantage_mode=effective_home_advantage_mode,
                    calibrate_probabilities=False
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

    def run_calibration_model_comparison(self, **kwargs):
        """
            Delegerar kalibreringsjämförelsen till
            BacktestCalibration.
        """
        return self.calibration.run_calibration_model_comparison(
            **kwargs
        )


    # --------------------------------------------------
    # Rho-diagnostik
    # --------------------------------------------------

    def run_rho_diagnostics(self, **kwargs):
        """
            Delegerar rho-diagnostiken till
            BacktestDiagnostics.
        """
        return self.diagnostics.run_rho_diagnostics(
            **kwargs
        )

    # --------------------------------------------------
    # Parameterjämförelser
    # --------------------------------------------------

    def run_rho_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_rho_comparison(
            **kwargs
        )

    def run_home_advantage_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_home_advantage_comparison(
            **kwargs
        )

    def run_time_decay_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_time_decay_comparison(
            **kwargs
        )

    def run_history_years_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_history_years_comparison(
            **kwargs
        )

    def run_training_scope_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_training_scope_comparison(
            **kwargs
        )

    def run_h2h_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_h2h_comparison(
            **kwargs
        )

    def run_form_match_count_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_form_match_count_comparison(
            **kwargs
        )

    def run_form_comparison(self, **kwargs):
        """
            Delegerar till BacktestParameterComparison.
        """
        return self.parameter_comparison.run_form_comparison(
            **kwargs
        )

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


