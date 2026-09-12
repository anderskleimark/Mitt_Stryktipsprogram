from decimal import Decimal

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

    OPTIMIZED_TIME_DECAY = 0.0027
    OPTIMIZED_HISTORY_YEARS = 3
    OPTIMIZED_TRAINING_SCOPE = AnalysisModel.TRAINING_SCOPE_COUNTRY

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    TRAINING_SCOPES = [
        AnalysisModel.TRAINING_SCOPE_COUNTRY,
        AnalysisModel.TRAINING_SCOPE_COMPETITION
    ]

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    FORM_MATCH_COUNT = 5

    # --------------------------------------------------
    # Inbördes möten
    # --------------------------------------------------

    H2H_MATCH_COUNT = 5

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

        self.view.copy_result_clicked.connect(
            self.on_copy_result_clicked
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
        self.selected_competition = (
            self.view.get_selected_competition()
        )

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
            Startar vald typ av backtest
            i en separat tråd.
        """
        if self.selected_season is None:
            return

        if self.backtest_thread is not None:
            return

        self.current_comparison_type = (
            self.view.get_selected_comparison_type()
        )

        if self.current_comparison_type is None:
            return

        time_decay_values = None
        history_years_values = None
        form_weights = None
        h2h_weights = None

        if (
            self.current_comparison_type
            == self.view.COMPARISON_TIME_DECAY
        ):
            try:
                time_decay_values = self._create_time_decay_values()

            except ValueError as error:
                print(f"Ogiltigt time-decay-intervall: {error}")
                return

        if (
            self.current_comparison_type
            == self.view.COMPARISON_HISTORY_YEARS
        ):
            try:
                history_years_values = (
                    self._create_history_years_values()
                )

            except ValueError as error:
                print(f"Ogiltigt historikintervall: {error}")
                return

        if self.current_comparison_type in (
            self.view.COMPARISON_FORM,
            self.view.COMPARISON_WORKER_BENCHMARK
        ):
            try:
                form_weights = self._create_form_weights()

            except ValueError as error:
                print(f"Ogiltigt formintervall: {error}")
                return

        if (
            self.current_comparison_type
            == self.view.COMPARISON_H2H
        ):
            try:
                h2h_weights = self._create_h2h_weights()

            except ValueError as error:
                print(f"Ogiltigt H2H-intervall: {error}")
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
            time_decay_values=time_decay_values,
            history_years_values=history_years_values,
            training_scopes=self.TRAINING_SCOPES,
            form_match_counts=[self.FORM_MATCH_COUNT],
            form_weights=form_weights,
            h2h_match_count=self.H2H_MATCH_COUNT,
            h2h_weights=h2h_weights,
            time_decay=self.OPTIMIZED_TIME_DECAY,
            history_years=self.OPTIMIZED_HISTORY_YEARS,
            training_scope=self.OPTIMIZED_TRAINING_SCOPE
        )

        self.backtest_worker.moveToThread(
            self.backtest_thread
        )

        self.backtest_thread.started.connect(
            self.backtest_worker.run
        )

        self.backtest_worker.progress.connect(
            self.view.set_backtest_progress
        )

        self.backtest_worker.finished.connect(
            self._store_backtest_results
        )

        self.backtest_worker.cancelled.connect(
            self._store_backtest_cancelled
        )

        self.backtest_worker.failed.connect(
            self._store_backtest_error
        )

        self.backtest_worker.completed.connect(
            self.backtest_thread.quit
        )

        self.backtest_worker.completed.connect(
            self.backtest_worker.deleteLater
        )

        self.backtest_thread.finished.connect(
            self._on_backtest_thread_finished
        )

        self.backtest_thread.start()

    # --------------------------------------------------
    # Time decay
    # --------------------------------------------------

    def _create_time_decay_values(self):
        """
            Skapar listan med time-decay-värden
            utifrån intervallet som valts i vyn.

            Decimal används för att undvika flyttalsfel
            vid upprepad addition.
        """
        minimum = Decimal(
            str(self.view.get_time_decay_min())
        )

        maximum = Decimal(
            str(self.view.get_time_decay_max())
        )

        step = Decimal(
            str(self.view.get_time_decay_step())
        )

        if step <= 0:
            raise ValueError(
                "Time-decay-steget måste vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Lägsta time decay får inte vara "
                "större än den högsta."
            )

        values = []
        value = minimum

        while value <= maximum:
            values.append(float(value))
            value += step

        if not values:
            raise ValueError(
                "Intervallet innehåller inga "
                "time-decay-värden."
            )

        return values

    # --------------------------------------------------
    # Historiklängd
    # --------------------------------------------------

    def _create_history_years_values(self):
        """
            Skapar listan med historiklängder
            utifrån intervallet som valts i vyn.
        """
        minimum = self.view.get_history_years_min()
        maximum = self.view.get_history_years_max()
        step = self.view.get_history_years_step()

        if step <= 0:
            raise ValueError(
                "Historiksteget måste vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Kortaste historiklängden får inte vara "
                "större än den längsta."
            )

        values = list(
            range(
                minimum,
                maximum + 1,
                step
            )
        )

        if not values:
            raise ValueError(
                "Intervallet innehåller inga "
                "historiklängder."
            )

        return values

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _create_form_weights(self):
        """
            Skapar listan med formvikter utifrån
            intervallet som valts i backtestvyn.

            Decimal används för att undvika flyttalsfel
            när exempelvis 0.01 adderas upprepade gånger.
        """
        minimum = Decimal(
            str(self.view.get_form_weight_min())
        )

        maximum = Decimal(
            str(self.view.get_form_weight_max())
        )

        step = Decimal(
            str(self.view.get_form_weight_step())
        )

        if step <= 0:
            raise ValueError(
                "Formsteget måste vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Lägsta formvikten får inte vara "
                "större än den högsta."
            )

        values = []
        value = minimum

        while value <= maximum:
            values.append(float(value))
            value += step

        if not values:
            raise ValueError(
                "Intervallet innehåller inga formvikter."
            )

        return values

    # --------------------------------------------------
    # Inbördes möten
    # --------------------------------------------------

    def _create_h2h_weights(self):
        """
            Skapar listan med H2H-vikter utifrån
            intervallet som valts i backtestvyn.

            Decimal används för att undvika flyttalsfel
            när exempelvis 0.01 adderas upprepade gånger.
        """
        minimum = Decimal(
            str(self.view.get_h2h_weight_min())
        )

        maximum = Decimal(
            str(self.view.get_h2h_weight_max())
        )

        step = Decimal(
            str(self.view.get_h2h_weight_step())
        )

        if step <= 0:
            raise ValueError(
                "H2H-steget måste vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Lägsta H2H-vikten får inte vara "
                "större än den högsta."
            )

        values = []
        value = minimum

        while value <= maximum:
            values.append(float(value))
            value += step

        if not values:
            raise ValueError(
                "Intervallet innehåller inga H2H-vikter."
            )

        return values

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

    def _on_backtest_thread_finished(self):
        """
            Schemalägger slutlig GUI-hantering efter att
            worker-tråden verkligen har avslutats.
        """
        thread = self.backtest_thread

        if thread is None:
            return

        QTimer.singleShot(
            0,
            lambda: self._finalize_backtest(thread)
        )

    def _finalize_backtest(self, thread):
        """
            Slutför backtestet och rensar QThread-objektet
            först efter att tråden har stannat helt.
        """
        if self.backtest_thread is not thread:
            return

        results = self._pending_results
        cancelled = self._pending_cancelled
        error = self._pending_error
        comparison_type = self.current_comparison_type

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

        elif cancelled:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()

        elif results is None:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()

        else:
            self.view.set_backtest_progress(100, "Klar")

            self.view.show_result(
                results,
                comparison_type
            )

        thread.deleteLater()

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
