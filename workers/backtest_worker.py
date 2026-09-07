import time
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from database.database import Database
from models.analysis.backtest_model import BacktestModel
from models.analysis_model import AnalysisModel
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

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    finished = Signal(object)
    cancelled = Signal()
    failed = Signal(str)

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
        time_decay=None,
        history_years=None,
        training_scope=None,
        form_match_count=None,
        form_weight=None,
        max_workers=None
    ):
        """
            Initierar workern med inställningar
            för vald backtestjämförelse.
        """
        super().__init__()

        self.season = season
        self.comparison_type = comparison_type

        self.time_decay_values = time_decay_values
        self.history_years_values = history_years_values
        self.training_scopes = training_scopes

        self.form_match_counts = form_match_counts
        self.form_weights = form_weights

        self.time_decay = time_decay
        self.history_years = history_years
        self.training_scope = training_scope

        self.form_match_count = form_match_count
        self.form_weight = form_weight

        self.max_workers = max_workers

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

            if (
                results is None
                or self._cancel_event.is_set()
            ):
                self.cancelled.emit()
                return

            elapsed_time = (
                time.monotonic()
                - self._start_time
            )

            print(
                f"Workers: {self.max_workers} | "
                f"Tid: {elapsed_time:.2f} s"
            )

            self.progress.emit(
                100,
                "Klar"
            )

            self.finished.emit(
                results
            )

        except Exception as error:
            self.failed.emit(
                str(error)
            )

        finally:
            if database is not None:
                database.close()

    def _run_comparison(
        self,
        backtest_model
    ):
        """
            Kör vald typ av
            backtestjämförelse.
        """
        if (
            self.comparison_type
            == self.COMPARISON_TIME_DECAY
        ):
            return self._run_time_decay_comparison(
                backtest_model
            )

        if (
            self.comparison_type
            == self.COMPARISON_HISTORY_YEARS
        ):
            return self._run_history_years_comparison(
                backtest_model
            )

        if (
            self.comparison_type
            == self.COMPARISON_TRAINING_SCOPE
        ):
            return self._run_training_scope_comparison(
                backtest_model
            )

        if (
            self.comparison_type
            == self.COMPARISON_FORM
        ):
            return self._run_form_comparison(
                backtest_model
            )

        raise ValueError(
            "Okänd typ av backtestjämförelse."
        )

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    def _run_time_decay_comparison(
        self,
        backtest_model
    ):
        """
            Kör jämförelse av olika
            time decay-värden.
        """
        if not self.time_decay_values:
            raise ValueError(
                "Inga time decay-värden har angetts."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd saknas."
            )

        if self.training_scope is None:
            raise ValueError(
                "Omfattning av träningsdata saknas."
            )

        return backtest_model.run_time_decay_comparison(
            season=self.season,
            time_decay_values=self.time_decay_values,
            history_years=self.history_years,
            training_scope=self.training_scope,
            form_match_count=self.form_match_count,
            form_weight=self.form_weight,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress,
            max_workers=self.max_workers
        )

    # --------------------------------------------------
    # Historiklängd
    # --------------------------------------------------

    def _run_history_years_comparison(
        self,
        backtest_model
    ):
        """
            Kör jämförelse av olika
            historiklängder.
        """
        if not self.history_years_values:
            raise ValueError(
                "Inga historiklängder har angetts."
            )

        if self.time_decay is None:
            raise ValueError(
                "Time decay saknas."
            )

        if self.training_scope is None:
            raise ValueError(
                "Omfattning av träningsdata saknas."
            )

        return backtest_model.run_history_years_comparison(
            season=self.season,
            history_years_values=self.history_years_values,
            time_decay=self.time_decay,
            training_scope=self.training_scope,
            form_match_count=self.form_match_count,
            form_weight=self.form_weight,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress,
            max_workers=self.max_workers
        )

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    def _run_training_scope_comparison(
        self,
        backtest_model
    ):
        """
            Kör jämförelse av olika
            omfattningar av träningsdata.
        """
        if not self.training_scopes:
            raise ValueError(
                "Inga omfattningar av träningsdata "
                "har angetts."
            )

        if self.time_decay is None:
            raise ValueError(
                "Time decay saknas."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd saknas."
            )

        return backtest_model.run_training_scope_comparison(
            season=self.season,
            training_scopes=self.training_scopes,
            time_decay=self.time_decay,
            history_years=self.history_years,
            form_match_count=self.form_match_count,
            form_weight=self.form_weight,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress,
            max_workers=self.max_workers
        )

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _run_form_comparison(
        self,
        backtest_model
    ):
        """
            Kör jämförelse av olika
            formfönster och formvikter.
        """
        if not self.form_match_counts:
            raise ValueError(
                "Inga antal formmatcher har angetts."
            )

        if not self.form_weights:
            raise ValueError(
                "Inga formvikter har angetts."
            )

        if self.time_decay is None:
            raise ValueError(
                "Time decay saknas."
            )

        if self.history_years is None:
            raise ValueError(
                "Historiklängd saknas."
            )

        if self.training_scope is None:
            raise ValueError(
                "Omfattning av träningsdata saknas."
            )

        return backtest_model.run_form_comparison(
            season=self.season,
            form_match_counts=self.form_match_counts,
            form_weights=self.form_weights,
            time_decay=self.time_decay,
            history_years=self.history_years,
            training_scope=self.training_scope,
            should_cancel=self._cancel_event.is_set,
            progress_callback=self._report_progress,
            max_workers=self.max_workers
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
            Rapporterar procentuell progress
            och uppskattad återstående tid.
        """
        if total <= 0:
            return

        percentage = int(
            completed * 100 / total
        )

        percentage = min(
            max(percentage, 0),
            100
        )

        if percentage == self._last_progress:
            return

        self._last_progress = percentage

        if (
            self._start_time is None
            or completed <= 0
        ):
            self.progress.emit(
                percentage,
                "Beräknar återstående tid..."
            )
            return

        elapsed_time = (
            time.monotonic()
            - self._start_time
        )

        average_time = (
            elapsed_time / completed
        )

        remaining_steps = max(
            total - completed,
            0
        )

        remaining_time = (
            average_time * remaining_steps
        )

        self.progress.emit(
            percentage,
            self._format_remaining_time(
                remaining_time
            )
        )

    @staticmethod
    def _format_remaining_time(
        seconds
    ):
        """
            Formaterar uppskattad
            återstående tid.
        """
        seconds = max(
            int(round(seconds)),
            0
        )

        if seconds < 60:
            return (
                f"Återstående tid: "
                f"{seconds} sek"
            )

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        if minutes < 60:
            return (
                f"Återstående tid: "
                f"{minutes} min "
                f"{remaining_seconds} sek"
            )

        hours = minutes // 60
        remaining_minutes = minutes % 60

        return (
            f"Återstående tid: "
            f"{hours} h "
            f"{remaining_minutes} min"
        )

    # --------------------------------------------------
    # Avbryt
    # --------------------------------------------------

    @Slot()
    def request_cancel(self):
        """
            Begär att pågående
            backtest ska avbrytas.
        """
        self._cancel_event.set()
