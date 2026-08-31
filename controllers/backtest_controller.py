from datetime import date

from PySide6.QtCore import QThread

from mvc import Controller
from workers.backtest_worker import BacktestWorker


class BacktestController(Controller):
    """
        Controller för historisk backtestning
        av matchanalysmodellen.
    """

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    TIME_DECAY_VALUES = [
        0.0030,
        0.0032,
        0.0034,
        0.0036,
        0.0038,
        0.0040,
        0.0042,
        0.0044,
        0.0046,
        0.0048,
        0.0050,
        0.0052,
        0.0054,
        0.0056
    ]

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(
        self,
        *,
        view,
        competition_model,
        soccer_model
    ):
        super().__init__(view)

        self.view = view

        self.competition_model = competition_model
        self.soccer_model = soccer_model

        self.competitions = []
        self.seasons = []

        self.selected_competition = None
        self.selected_season = None

        self.backtest_thread = None
        self.backtest_worker = None

        self._setup_signals()
        self.initialize()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar vyens signaler till
            controllern.
        """
        self.view.competition_changed.connect(
            self.on_competition_changed
        )

        self.view.season_changed.connect(
            self.on_season_changed
        )

        self.view.run_clicked.connect(
            self.on_run_clicked
        )

        self.view.cancel_clicked.connect(
            self.on_cancel_clicked
        )

        self.view.back_clicked.connect(
            self.on_back_clicked
        )

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def initialize(self):
        """
            Initierar vyn med tillgängliga
            tävlingar.
        """
        self.competitions = (
            self.competition_model.get_all()
        )

        self.view.fill_competition_combo(
            self.competitions
        )

        self._update_run_button()

    # --------------------------------------------------
    # Tävling
    # --------------------------------------------------

    def on_competition_changed(self):
        """
            Hanterar byte av tävling.
        """
        self.selected_competition = (
            self.view.get_selected_competition()
        )

        self.selected_season = None
        self.seasons = []

        self.view.clear_result()

        if self.selected_competition is None:
            self.view.fill_season_combo(
                []
            )

            self._update_run_button()
            return

        self.seasons = (
            self.soccer_model.get_seasons(
                competition_id=(
                    self.selected_competition.id
                )
            )
        )

        self.view.fill_season_combo(
            self.seasons
        )

        self._update_run_button()

    # --------------------------------------------------
    # Säsong
    # --------------------------------------------------

    def on_season_changed(self):
        """
            Hanterar byte av säsong.
        """
        self.selected_season = (
            self.view.get_selected_season()
        )

        self.view.clear_result()

        if self.selected_season is not None:
            self.view.set_date_range(
                self._get_season_start_date(),
                self._get_season_end_date()
            )

        self._update_run_button()

    # --------------------------------------------------
    # Backtest
    # --------------------------------------------------

    def on_run_clicked(self):
        """
            Startar ett backtest med flera
            time-decay-värden i separat tråd.
        """
        if self.selected_season is None:
            return

        if self.backtest_thread is not None:
            return

        start_date = (
            self.view.get_start_date()
        )

        end_date = (
            self.view.get_end_date()
        )

        if start_date >= end_date:
            return

        self.view.clear_result()

        self.view.reset_backtest_progress()

        self.view.set_progress_visible(
            True
        )

        self.view.set_backtest_running(
            True
        )

        self.backtest_thread = QThread()

        self.backtest_worker = BacktestWorker(
            season=self.selected_season,
            start_date=start_date,
            end_date=end_date,
            time_decay_values=(
                self.TIME_DECAY_VALUES
            )
        )

        self.backtest_worker.moveToThread(
            self.backtest_thread
        )

        # Start.
        self.backtest_thread.started.connect(
            self.backtest_worker.run
        )

        # Progress.
        self.backtest_worker.progress.connect(
            self.view.set_backtest_progress
        )

        # Resultat.
        self.backtest_worker.finished.connect(
            self.on_backtest_finished
        )

        self.backtest_worker.cancelled.connect(
            self.on_backtest_cancelled
        )

        self.backtest_worker.failed.connect(
            self.on_backtest_failed
        )

        # Avsluta tråden.
        self.backtest_worker.finished.connect(
            self.backtest_thread.quit
        )

        self.backtest_worker.cancelled.connect(
            self.backtest_thread.quit
        )

        self.backtest_worker.failed.connect(
            self.backtest_thread.quit
        )

        # Rensa Qt-objekt.
        self.backtest_thread.finished.connect(
            self.backtest_worker.deleteLater
        )

        self.backtest_thread.finished.connect(
            self.backtest_thread.deleteLater
        )

        self.backtest_thread.finished.connect(
            self._cleanup_backtest
        )

        self.backtest_thread.start()

    def on_cancel_clicked(self):
        """
            Begär att pågående backtest
            ska avbrytas.
        """
        if self.backtest_worker is None:
            return

        self.backtest_worker.request_cancel()

        self.view.set_cancel_button_status(
            False
        )

    def on_backtest_finished(
        self,
        results
    ):
        """
            Hanterar ett färdigkört
            backtest.
        """
        self.view.set_backtest_running(
            False
        )

        self.view.set_backtest_progress(
            100,
            "Klar"
        )

        self._update_run_button()

        self.view.show_result(
            results
        )

    def on_backtest_cancelled(self):
        """
            Hanterar ett avbrutet
            backtest.
        """
        self.view.set_backtest_running(
            False
        )

        self.view.set_progress_visible(
            False
        )

        self.view.reset_backtest_progress()

        self._update_run_button()

    def on_backtest_failed(
        self,
        message
    ):
        """
            Hanterar fel under
            backtestkörningen.
        """
        self.view.set_backtest_running(
            False
        )

        self.view.set_progress_visible(
            False
        )

        self.view.reset_backtest_progress()

        self._update_run_button()

        print(
            f"Backtest misslyckades: "
            f"{message}"
        )

    def on_back_clicked(self):
        """
            Går från jämförelsen tillbaka
            till backtestinställningarna.
        """
        self.view.show_settings()

    # --------------------------------------------------
    # Datum
    # --------------------------------------------------

    def _get_season_start_date(self):
        """
            Returnerar säsongens ungefärliga
            startdatum.
        """
        return date(
            self.selected_season.start_year,
            1,
            1
        )

    def _get_season_end_date(self):
        """
            Returnerar säsongens ungefärliga
            slutdatum.
        """
        return date(
            self.selected_season.end_year + 1,
            1,
            1
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def _update_run_button(self):
        """
            Uppdaterar status för
            backtestknappen.
        """
        self.view.set_run_button_status(
            (
                self.selected_season is not None
                and self.backtest_thread is None
            )
        )

    def _cleanup_backtest(self):
        """
            Rensar referenser efter
            avslutad backtestkörning.
        """
        self.backtest_worker = None
        self.backtest_thread = None

        self._update_run_button()
