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
        start_date,
        end_date,
        time_decay_values
    ):
        super().__init__()

        self.season = season

        self.start_date = start_date
        self.end_date = end_date

        self.time_decay_values = (
            time_decay_values
        )

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

            # Starta tidtagningen.
            self._start_time = (
                time.monotonic()
            )

            self._last_progress = -1

            # Visa 0 % direkt.
            self.progress.emit(
                0,
                "Beräknar återstående tid..."
            )

            results = (
                backtest_model
                .run_time_decay_comparison(
                    season=self.season,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    time_decay_values=(
                        self.time_decay_values
                    ),
                    should_cancel=(
                        self._cancel_event.is_set
                    ),
                    progress_callback=(
                        self._report_progress
                    )
                )
            )

            if (
                results is None
                or self._cancel_event.is_set()
            ):
                self.cancelled.emit()
                return

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

        # Skicka bara en signal när procenten
        # faktiskt har förändrats.
        if percent == self._last_progress:
            return

        self._last_progress = percent

        if (
            self._start_time is None
            or completed <= 0
        ):
            remaining_text = (
                "Beräknar återstående tid..."
            )

        else:
            elapsed = (
                time.monotonic()
                - self._start_time
            )

            seconds_per_step = (
                elapsed
                / completed
            )

            remaining_seconds = (
                seconds_per_step
                * (total - completed)
            )

            remaining_text = (
                self._format_remaining_time(
                    remaining_seconds
                )
            )

        self.progress.emit(
            percent,
            remaining_text
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
            Begär att pågående backtest
            ska avbrytas.
        """
        self._cancel_event.set()
