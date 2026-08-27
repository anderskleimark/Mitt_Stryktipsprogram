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
            # Viktigt:
            # Databasanslutningen skapas här,
            # alltså inne i worker-tråden.
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
                    )
                )
            )

            if (
                results is None
                or self._cancel_event.is_set()
            ):
                self.cancelled.emit()
                return

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
    # Avbryt
    # --------------------------------------------------

    def request_cancel(self):
        """
            Begär att pågående backtest
            ska avbrytas.
        """
        self._cancel_event.set()
