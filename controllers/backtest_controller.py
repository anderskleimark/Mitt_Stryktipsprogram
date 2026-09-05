from PySide6.QtCore import QThread, QTimer
from models.analysis_model import AnalysisModel
from mvc import Controller
from workers.backtest_worker import BacktestWorker


class BacktestController(Controller):
    """
        Controller för historisk backtestning
        av matchanalysmodellen.
    """

    # --------------------------------------------------
    # Optimerade värden
    # --------------------------------------------------

    OPTIMIZED_TIME_DECAY = 0.0025
    OPTIMIZED_HISTORY_YEARS = 3
    OPTIMIZED_TRAINING_SCOPE = AnalysisModel.TRAINING_SCOPE_COUNTRY

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    TIME_DECAY_VALUES = [
        0.0020,
        0.0021,
        0.0022,
        0.0023,
        0.0024,
        0.0025,
        0.0026,
        0.0027,
        0.0028,
        0.0029,
        0.0030
    ]

    # --------------------------------------------------
    # Historiklängd
    # --------------------------------------------------

    HISTORY_YEARS_VALUES = [
        3,
        4
    ]

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    TRAINING_SCOPES = [
        AnalysisModel.TRAINING_SCOPE_COUNTRY,
        AnalysisModel.TRAINING_SCOPE_COMPETITION
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

        self.current_comparison_type = None

        self.backtest_thread = None
        self.backtest_worker = None

        self._pending_results = None
        self._pending_cancelled = False
        self._pending_error = None

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
        self.view.competition_changed.connect(self.on_competition_changed)
        self.view.season_changed.connect(self.on_season_changed)
        self.view.run_clicked.connect(self.on_run_clicked)
        self.view.cancel_clicked.connect(self.on_cancel_clicked)
        self.view.copy_result_clicked.connect(self.on_copy_result_clicked)
        self.view.back_clicked.connect(self.on_back_clicked)

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def initialize(self):
        """
            Initierar vyn med tillgängliga
            tävlingar.
        """
        self.competitions = self.competition_model.get_all()
        self.view.fill_competition_combo(self.competitions)
        self._update_run_button()

    # --------------------------------------------------
    # Tävling
    # --------------------------------------------------

    def on_competition_changed(self):
        """
            Hanterar byte av tävling.
        """
        self.selected_competition = self.view.get_selected_competition()

        self.selected_season = None
        self.seasons = []

        self.view.clear_result()

        if self.selected_competition is None:
            self.view.fill_season_combo([])
            self._update_run_button()
            return

        self.seasons = self.soccer_model.get_seasons(
            competition_id=self.selected_competition.id
        )

        self.view.fill_season_combo(self.seasons)
        self._update_run_button()

    # --------------------------------------------------
    # Säsong
    # --------------------------------------------------

    def on_season_changed(self):
        """
            Hanterar byte av säsong.
        """
        self.selected_season = self.view.get_selected_season()

        self.view.clear_result()

        self._update_run_button()

    # --------------------------------------------------
    # Backtest
    # --------------------------------------------------

    def on_run_clicked(self):
        """
            Startar vald typ av backtest i en separat tråd.
        """
        if self.selected_season is None:
            return

        if self.backtest_thread is not None:
            return

        self.current_comparison_type = self.view.get_selected_comparison_type()

        if self.current_comparison_type is None:
            return

        self._pending_results = None
        self._pending_cancelled = False
        self._pending_error = None

        self.view.reset_backtest_progress()
        self.view.set_progress_visible(True)
        self.view.set_backtest_running(True)

        self.backtest_thread = QThread()

        self.backtest_worker = BacktestWorker(
            season=self.selected_season,
            comparison_type=self.current_comparison_type,
            time_decay_values=self.TIME_DECAY_VALUES,
            history_years_values=self.HISTORY_YEARS_VALUES,
            training_scopes=self.TRAINING_SCOPES,
            time_decay=self.OPTIMIZED_TIME_DECAY,
            history_years=self.OPTIMIZED_HISTORY_YEARS,
            training_scope=self.OPTIMIZED_TRAINING_SCOPE
        )

        self.backtest_worker.moveToThread(self.backtest_thread)

        # Start.
        self.backtest_thread.started.connect(self.backtest_worker.run)

        # Progress.
        self.backtest_worker.progress.connect(self.view.set_backtest_progress)

        # Spara resultat/status. Vyn uppdateras först när
        # worker-tråden verkligen har avslutats.
        self.backtest_worker.finished.connect(self._store_backtest_results)
        self.backtest_worker.cancelled.connect(self._store_backtest_cancelled)
        self.backtest_worker.failed.connect(self._store_backtest_error)

        # Avsluta worker-tråden.
        self.backtest_worker.finished.connect(self.backtest_thread.quit)
        self.backtest_worker.cancelled.connect(self.backtest_thread.quit)
        self.backtest_worker.failed.connect(self.backtest_thread.quit)

        # Standardmönster för säker QObject-rensning.
        self.backtest_worker.finished.connect(self.backtest_worker.deleteLater)
        self.backtest_worker.cancelled.connect(
            self.backtest_worker.deleteLater)
        self.backtest_worker.failed.connect(self.backtest_worker.deleteLater)

        # Hantera GUI och rensa trådobjekt först när tråden
        # faktiskt är helt färdig.
        self.backtest_thread.finished.connect(
            self._schedule_backtest_thread_finished)

        self.backtest_thread.start()

    def on_cancel_clicked(self):
        """
            Begär att pågående backtest
            ska avbrytas.
        """
        if self.backtest_worker is None:
            return

        self.backtest_worker.request_cancel()
        self.view.set_cancel_button_status(False)

    def _store_backtest_results(self, results):
        """
            Sparar backtestresultatet tills
            worker-tråden har avslutats.
        """
        self._pending_results = results

    def _store_backtest_cancelled(self):
        """
            Markerar att backtestet
            har avbrutits.
        """
        self._pending_cancelled = True

    def _store_backtest_error(self, message):
        """
            Sparar ett fel tills worker-tråden
            har avslutats.
        """
        self._pending_error = message

    def _schedule_backtest_thread_finished(self):
        """
            Schemalägger slutlig hantering till
            nästa varv i huvudtrådens eventloop.
        """
        QTimer.singleShot(
            0,
            self._on_backtest_thread_finished
        )

    def _on_backtest_thread_finished(self):
        """
            Slutför backtestet när worker-tråden är helt avslutad.
        """
        results = self._pending_results
        cancelled = self._pending_cancelled
        error = self._pending_error

        self.backtest_worker = None
        self.backtest_thread = None

        self._pending_results = None
        self._pending_cancelled = False
        self._pending_error = None

        self.view.set_backtest_running(False)
        self._update_run_button()

        if error is not None:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()
            print(f"Backtest misslyckades: {error}")
            return

        if cancelled:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()
            return

        if results is None:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()
            return

        self.view.set_backtest_progress(100, "Klar")

        self.view.show_result(
            results,
            self.current_comparison_type
        )

    # --------------------------------------------------
    # Kopiering
    # --------------------------------------------------

    def on_copy_result_clicked(self):
        """
            Hanterar begäran att kopiera
            aktuellt backtestresultat.
        """
        self.view.copy_result()

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def on_back_clicked(self):
        """
            Går från jämförelsen tillbaka
            till backtestinställningarna.
        """
        if self.backtest_thread is not None:
            return

        self.view.show_settings()

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def _update_run_button(self):
        """
            Uppdaterar status för
            backtestknappen.
        """
        self.view.set_run_button_status(
            self.selected_season is not None
            and self.backtest_thread is None
        )
