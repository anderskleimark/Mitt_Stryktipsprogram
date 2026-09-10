import time
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from database.database import Database
from models.analysis_model import AnalysisModel
from models.analysis.backtest_model import BacktestModel
from models.soccer_model import SoccerModel


class BacktestWorker(QObject):
    """
        Kör backtestningen i en separat tråd.

        Workern skapar en egen databasanslutning
        eftersom SQLite-anslutningar inte ska
        delas mellan trådar.
    """

    # --------------------------------------------------
    # Jämförelsetyper
    # --------------------------------------------------

    COMPARISON_TIME_DECAY = "time_decay"
    COMPARISON_HISTORY_YEARS = "history_years"
    COMPARISON_TRAINING_SCOPE = "training_scope"
    COMPARISON_FORM = "form"
    COMPARISON_H2H = "h2h"
    COMPARISON_RHO_DIAGNOSTICS = "rho_diagnostics"
    COMPARISON_RHO_COMPARISON = "rho_comparison"

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    finished = Signal(object)
    cancelled = Signal()
    failed = Signal(str)

    # Skickas alltid sist, efter att databasanslutningen
    # har stängts och run() är färdig med allt arbete.
    completed = Signal()

    progress = Signal(
        int,
        str
    )

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

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

            Slutstatus skickas först efter att databasanslutningen
            har stängts. Det förhindrar att QObject/QThread rensas
            medan run() fortfarande håller på att avslutas.
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

            results = self._run_comparison(backtest_model)

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
                self.progress.emit(
                    100,
                    "Klar"
                )

                self.finished.emit(results)

        finally:
            # Den här signalen är den enda som får avsluta/rensa
            # worker-tråden i controllern.
            self.completed.emit()

    def _run_comparison(self, backtest_model):
        """
            Kör vald typ av backtestjämförelse.
        """
        if self.comparison_type == self.COMPARISON_TIME_DECAY:
            return self._run_time_decay_comparison(backtest_model)

        if self.comparison_type == self.COMPARISON_HISTORY_YEARS:
            return self._run_history_years_comparison(backtest_model)

        if self.comparison_type == self.COMPARISON_TRAINING_SCOPE:
            return self._run_training_scope_comparison(backtest_model)

        if self.comparison_type == self.COMPARISON_FORM:
            return self._run_form_comparison(backtest_model)

        if self.comparison_type == self.COMPARISON_H2H:
            return self._run_h2h_comparison(backtest_model)

        if self.comparison_type == self.COMPARISON_RHO_DIAGNOSTICS:
            return self._run_rho_diagnostics(backtest_model)

        if self.comparison_type == self.COMPARISON_RHO_COMPARISON:
            return self._run_rho_comparison(backtest_model)

        raise ValueError("Okänd typ av backtestjämförelse.")

    def _run_time_decay_comparison(self, backtest_model):
        """
            Kör jämförelse av olika
            time-decay-värden.
        """
        if not self.time_decay_values:
            raise ValueError("Inga time-decay-värden har angetts.")

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid "
                "jämförelse av time decay."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid "
                "jämförelse av time decay."
            )

        return backtest_model.run_time_decay_comparison(
            season=self.season,
            time_decay_values=self.time_decay_values,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    def _run_history_years_comparison(self, backtest_model):
        """
            Kör jämförelse av olika
            historiklängder.
        """
        if not self.history_years_values:
            raise ValueError("Inga historiklängder har angetts.")

        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid "
                "jämförelse av historiklängd."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid "
                "jämförelse av historiklängd."
            )

        return backtest_model.run_history_years_comparison(
            season=self.season,
            history_years_values=self.history_years_values,
            time_decay=self.time_decay,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    def _run_training_scope_comparison(self, backtest_model):
        """
            Kör jämförelse av olika
            omfattningar av träningsdata.
        """
        if not self.training_scopes:
            raise ValueError("Inga träningsomfattningar har angetts.")

        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid "
                "jämförelse av träningsdata."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid "
                "jämförelse av träningsdata."
            )

        return backtest_model.run_training_scope_comparison(
            season=self.season,
            training_scopes=self.training_scopes,
            time_decay=self.time_decay,
            history_years=self.history_years,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress
        )

    def _run_form_comparison(self, backtest_model):
        """
            Kör jämförelse av olika
            formparametrar.
        """
        if not self.form_match_counts:
            raise ValueError("Inga antal formmatcher har angetts.")

        if not self.form_weights:
            raise ValueError("Inga formvikter har angetts.")

        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid "
                "jämförelse av form."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid "
                "jämförelse av form."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid "
                "jämförelse av form."
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

    def _run_h2h_comparison(self, backtest_model):
        """
            Kör jämförelse av olika H2H-vikter.
        """
        if not self.h2h_weights:
            raise ValueError("Inga H2H-vikter har angetts.")

        if self.h2h_match_count is None:
            raise ValueError("Antal H2H-matcher måste anges.")

        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid H2H-jämförelse."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid H2H-jämförelse."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid H2H-jämförelse."
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

    def _run_rho_comparison(self, backtest_model):
        """
            Jämför fritt skattad rho med rho = 0.0.
        """
        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid rho-jämförelse."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid rho-jämförelse."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid rho-jämförelse."
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
            Kör diagnostik av rho-värdena som
            skattas av Dixon-Coles-modellen.
        """
        if self.time_decay is None:
            raise ValueError(
                "Time decay måste anges vid rho-diagnostik."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd måste anges vid rho-diagnostik."
            )

        if self.training_scope is None:
            raise ValueError(
                "Träningsdata måste anges vid rho-diagnostik."
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
    # Progress
    # --------------------------------------------------

    def _report_progress(
        self,
        completed,
        total
    ):
        """
            Rapporterar procent och uppskattad
            återstående tid.
        """
        if total <= 0:
            return

        percent = int(
            completed
            * 100
            / total
        )

        if percent == self._last_progress:
            return

        self._last_progress = percent

        if self._start_time is None or completed <= 0:
            remaining_text = "Beräknar återstående tid..."

        else:
            elapsed = time.monotonic() - self._start_time
            seconds_per_step = elapsed / completed
            remaining_seconds = seconds_per_step * (total - completed)
            remaining_text = self._format_remaining_time(remaining_seconds)

        self.progress.emit(
            percent,
            remaining_text
        )

    @staticmethod
    def _format_remaining_time(seconds):
        """
            Formaterar uppskattad
            återstående tid.
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

        return f"Beräknad tid kvar: {seconds} s"

    # --------------------------------------------------
    # Avbryt
    # --------------------------------------------------

    def request_cancel(self):
        """
            Begär att pågående backtest
            ska avbrytas.
        """
        self._cancel_event.set()
