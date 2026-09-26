import time
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from database.database import Database
from models.backtest.backtest_model import BacktestModel
from models.analysis.analysis_model import AnalysisModel
from models.backtest.backtest_types import BacktestComparison
from models.soccer_model import SoccerModel


class BacktestWorker(QObject):
    """
        Kör backtestning i en separat tråd.
    """

    finished = Signal(object)
    cancelled = Signal()
    failed = Signal(str)
    completed = Signal()
    progress = Signal(int, str)

    def __init__(
        self,
        *,
        season,
        comparison_type,
        time_decay_values=None,
        history_years_values=None,
        training_scopes=None,
        form_match_counts=None,
        form_weights=None,
        form_weight=None,
        h2h_match_count=None,
        h2h_weights=None,
        time_decay=None,
        history_years=None,
        training_scope=None
    ):
        super().__init__()

        self.season = season
        self.comparison_type = comparison_type

        self.time_decay_values = time_decay_values
        self.history_years_values = history_years_values
        self.training_scopes = training_scopes

        self.form_match_counts = form_match_counts
        self.form_weights = form_weights
        self.form_weight = form_weight

        self.h2h_match_count = h2h_match_count
        self.h2h_weights = h2h_weights

        self.time_decay = time_decay
        self.history_years = history_years
        self.training_scope = training_scope

        self._cancel_event = Event()
        self._start_time = None
        self._last_progress = -1

    # --------------------------------------------------
    # Körning
    # --------------------------------------------------

    @Slot()
    def run(self):
        """
            Genomför backtestet i worker-tråden.
        """
        database = None
        results = None
        error_message = None

        try:
            database = Database(initialize=False)
            soccer_model = SoccerModel(database)

            analysis_model = AnalysisModel(
                database,
                soccer_model
            )

            backtest_model = BacktestModel(
                soccer_model=soccer_model,
                analysis_model=analysis_model
            )

            self._start_time = time.monotonic()
            self._last_progress = -1

            self.progress.emit(
                0,
                "Beräknar återstående tid..."
            )

            results = self._run_comparison(
                backtest_model
            )

        except Exception as error:
            error_message = str(error)

        finally:
            if database is not None:
                database.close()

        try:
            if error_message is not None:
                self.failed.emit(error_message)

            elif results is None or self._cancel_event.is_set():
                self.cancelled.emit()

            else:
                self.progress.emit(100, "Klar")
                self.finished.emit(results)

        finally:
            self.completed.emit()

    def _run_comparison(self, backtest_model):
        """
            Kör vald typ av backtestjämförelse.
        """
        if self.comparison_type == BacktestComparison.TIME_DECAY:
            return self._run_time_decay_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.HISTORY_YEARS:
            return self._run_history_years_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.TRAINING_SCOPE:
            return self._run_training_scope_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.FORM:
            return self._run_form_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.FORM_MATCH_COUNT:
            return self._run_form_match_count_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.H2H:
            return self._run_h2h_comparison(backtest_model)


        if self.comparison_type == BacktestComparison.RHO_DIAGNOSTICS:
            return self._run_rho_diagnostics(backtest_model)

        if self.comparison_type == BacktestComparison.RHO_COMPARISON:
            return self._run_rho_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.HOME_ADVANTAGE:
            return self._run_home_advantage_comparison(backtest_model)

        if self.comparison_type == BacktestComparison.CALIBRATION_MODEL:
            return self._run_calibration_model_comparison(backtest_model)

        raise ValueError(
            f"Okänd typ av backtestjämförelse: "
            f"{self.comparison_type}"
        )

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    def _run_time_decay_comparison(self, backtest_model):
        """
            Kör jämförelse av olika time-decay-värden.
        """
        if not self.time_decay_values:
            raise ValueError(
                "Inga time-decay-värden har angetts."
            )

        self._validate_history_years(
            "jämförelse av time decay"
        )

        self._validate_training_scope(
            "jämförelse av time decay"
        )

        return backtest_model.run_time_decay_comparison(
            season=self.season,
            time_decay_values=self.time_decay_values,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Historiklängd
    # --------------------------------------------------

    def _run_history_years_comparison(self, backtest_model):
        """
            Kör jämförelse av olika historiklängder.
        """
        if not self.history_years_values:
            raise ValueError(
                "Inga historiklängder har angetts."
            )

        self._validate_time_decay(
            "jämförelse av historiklängd"
        )

        self._validate_training_scope(
            "jämförelse av historiklängd"
        )

        return backtest_model.run_history_years_comparison(
            season=self.season,
            history_years_values=self.history_years_values,
            time_decay=self.time_decay,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    def _run_training_scope_comparison(self, backtest_model):
        """
            Kör jämförelse av olika omfattningar
            av träningsdata.
        """
        if not self.training_scopes:
            raise ValueError(
                "Inga träningsomfattningar har angetts."
            )

        self._validate_time_decay(
            "jämförelse av träningsdata"
        )

        self._validate_history_years(
            "jämförelse av träningsdata"
        )

        return backtest_model.run_training_scope_comparison(
            season=self.season,
            training_scopes=self.training_scopes,
            time_decay=self.time_decay,
            history_years=self.history_years,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _run_form_comparison(self, backtest_model):
        """
            Kör jämförelse av olika formvikter.
        """
        if not self.form_match_counts:
            raise ValueError(
                "Antal formmatcher har inte angetts."
            )

        if not self.form_weights:
            raise ValueError(
                "Inga formvikter har angetts."
            )

        self._validate_standard_settings(
            "jämförelse av form"
        )

        return backtest_model.run_form_comparison(
            season=self.season,
            form_match_counts=self.form_match_counts,
            form_weights=self.form_weights,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    def _run_form_match_count_comparison(
        self,
        backtest_model
    ):
        """
            Jämför olika antal formmatcher
            med fast formvikt.
        """
        if not self.form_match_counts:
            raise ValueError(
                "Inga antal formmatcher har angetts."
            )

        if self.form_weight is None:
            raise ValueError(
                "Formvikt måste anges."
            )

        self._validate_standard_settings(
            "jämförelse av antal formmatcher"
        )

        return backtest_model.run_form_match_count_comparison(
            season=self.season,
            form_match_counts=self.form_match_counts,
            form_weight=self.form_weight,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # H2H
    # --------------------------------------------------

    def _run_h2h_comparison(self, backtest_model):
        """
            Kör jämförelse av olika H2H-vikter.
        """
        if not self.h2h_weights:
            raise ValueError(
                "Inga H2H-vikter har angetts."
            )

        if self.h2h_match_count is None:
            raise ValueError(
                "Antal H2H-matcher måste anges."
            )

        self._validate_standard_settings(
            "H2H-jämförelse"
        )

        return backtest_model.run_h2h_comparison(
            season=self.season,
            h2h_match_count=self.h2h_match_count,
            h2h_weights=self.h2h_weights,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )


    # --------------------------------------------------
    # Rho
    # --------------------------------------------------

    def _run_rho_comparison(self, backtest_model):
        """
            Jämför skattad rho med rho = 0.0.
        """
        self._validate_standard_settings(
            "rho-jämförelse"
        )

        return backtest_model.run_rho_comparison(
            season=self.season,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    def _run_rho_diagnostics(self, backtest_model):
        """
            Kör diagnostik av skattade rho-värden.
        """
        self._validate_standard_settings(
            "rho-diagnostik"
        )

        return backtest_model.run_rho_diagnostics(
            season=self.season,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Hemmafördel
    # --------------------------------------------------

    def _run_home_advantage_comparison(
        self,
        backtest_model
    ):
        """
            Jämför skattad hemmafördel med
            hemmafördel = 0.0.
        """
        self._validate_standard_settings(
            "hemmafördels-jämförelse"
        )

        return backtest_model.run_home_advantage_comparison(
            season=self.season,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            form_match_count=(
                self._get_form_match_count()
            ),
            form_weight=self.form_weight,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Kalibreringsmodell
    # --------------------------------------------------

    def _run_calibration_model_comparison(
        self,
        backtest_model
    ):
        """
            Jämför okalibrerade, globala och
            ligaspecifikt kalibrerade sannolikheter.
        """
        self._validate_standard_settings(
            "kalibreringsjämförelse"
        )

        return backtest_model.run_calibration_model_comparison(
            season=self.season,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            form_match_count=self._get_form_match_count(),
            form_weight=self.form_weight,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    # --------------------------------------------------
    # Inställningar
    # --------------------------------------------------

    def _get_form_match_count(self):
        """
            Returnerar fast antal formmatcher
            om exakt ett värde har angetts.
        """
        if not self.form_match_counts:
            return None

        if len(self.form_match_counts) == 1:
            return self.form_match_counts[0]

        return None

    # --------------------------------------------------
    # Validering
    # --------------------------------------------------

    def _validate_standard_settings(
        self,
        comparison_name
    ):
        """
            Validerar de tre grundinställningarna
            som används av de flesta jämförelser.
        """
        self._validate_time_decay(
            comparison_name
        )

        self._validate_history_years(
            comparison_name
        )

        self._validate_training_scope(
            comparison_name
        )

    def _validate_time_decay(self, comparison_name):
        if self.time_decay is None:
            raise ValueError(
                f"Time decay måste anges vid "
                f"{comparison_name}."
            )

    def _validate_history_years(
        self,
        comparison_name
    ):
        if self.history_years is None:
            raise ValueError(
                f"Historiklängd måste anges vid "
                f"{comparison_name}."
            )

    def _validate_training_scope(
        self,
        comparison_name
    ):
        if self.training_scope is None:
            raise ValueError(
                f"Träningsdata måste anges vid "
                f"{comparison_name}."
            )

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def _report_progress(self, completed, total):
        """
            Rapporterar procent och uppskattad
            återstående tid.
        """
        if total <= 0:
            return

        percent = int(
            completed * 100 / total
        )

        if percent == self._last_progress:
            return

        self._last_progress = percent

        if self._start_time is None or completed <= 0:
            remaining_text = (
                "Beräknar återstående tid..."
            )

        else:
            elapsed = time.monotonic() - self._start_time
            seconds_per_step = elapsed / completed

            remaining_seconds = (
                seconds_per_step
                * (total - completed)
            )

            remaining_text = self._format_remaining_time(
                remaining_seconds
            )

        self.progress.emit(
            percent,
            remaining_text
        )

    @staticmethod
    def _format_remaining_time(seconds):
        """
            Formaterar uppskattad återstående tid.
        """
        seconds = max(
            0,
            int(round(seconds))
        )

        minutes, seconds = divmod(
            seconds,
            60
        )

        hours, minutes = divmod(
            minutes,
            60
        )

        if hours > 0:
            return (
                f"Beräknad tid kvar: "
                f"{hours} h {minutes} min"
            )

        if minutes > 0:
            return (
                f"Beräknad tid kvar: "
                f"{minutes} min {seconds} s"
            )

        return (
            f"Beräknad tid kvar: "
            f"{seconds} s"
        )

    # --------------------------------------------------
    # Avbryt
    # --------------------------------------------------

    def request_cancel(self):
        """
            Begär att pågående backtest ska avbrytas.
        """
        self._cancel_event.set()
