from decimal import Decimal

from PySide6.QtCore import QThread, QTimer

from models.analysis.analysis_model import AnalysisModel
from models.backtest.backtest_types import BacktestComparison, TrainingScope
from mvc import Controller
from workers.backtest_worker import BacktestWorker


class BacktestController(Controller):
    """
        Hanterar backtestvyn och startar backtester
        i en separat worker-tråd.
    """

    # --------------------------------------------------
    # Optimerade modellinställningar
    # --------------------------------------------------

    OPTIMIZED_TIME_DECAY = 0.0027
    OPTIMIZED_HISTORY_YEARS = 3
    OPTIMIZED_TRAINING_SCOPE = TrainingScope.COUNTRY.value

    OPTIMIZED_FORM_MATCH_COUNT = AnalysisModel.FORM_MATCH_COUNT
    OPTIMIZED_FORM_WEIGHT = AnalysisModel.FORM_WEIGHT

    H2H_MATCH_COUNT = AnalysisModel.H2H_MATCH_COUNT

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(
        self,
        *,
        view,
        competition_model,
        soccer_model,
        main_window
    ):
        super().__init__(view)

        self.view = view
        self.competition_model = competition_model
        self.soccer_model = soccer_model
        self.main_window = main_window

        self.competitions = []
        self.seasons = []

        self.selected_competition = None
        self.selected_season = None
        self.current_comparison_type = None

        self.backtest_thread = None
        self.backtest_worker = None
        self._close_when_finished = False

        self._pending_results = None
        self._pending_cancelled = False
        self._pending_error = None

        self._connect_signals()
        self.initialize()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _connect_signals(self):
        """
            Kopplar vyens signaler till controllern.
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
            Hämtar tävlingarna och fyller vyn.
        """
        self.competitions = self.competition_model.get_all()

        self.view.fill_competition_combo(
            self.competitions
        )

        self._update_run_button()

    # --------------------------------------------------
    # Tävling och säsong
    # --------------------------------------------------

    def on_competition_changed(self):
        """
            Uppdaterar tillgängliga säsonger när
            användaren väljer en tävling.
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

        self.view.fill_season_combo(
            self.seasons
        )

        self._update_run_button()

    def on_season_changed(self):
        """
            Uppdaterar vald säsong.
        """
        self.selected_season = (
            self.view.get_selected_season()
        )

        self.view.clear_result()
        self._update_run_button()

    # --------------------------------------------------
    # Starta backtest
    # --------------------------------------------------

    def on_run_clicked(self):
        """
            Startar vald backtestjämförelse.
        """
        if self.selected_season is None:
            return

        if self.backtest_thread is not None:
            return

        self.current_comparison_type = self.view.get_selected_comparison_type()

        if self.current_comparison_type is None:
            return

        try:
            worker_settings = (
                self._create_worker_settings(self.current_comparison_type)
            )

        except ValueError as error:
            print(f"Backtestet kunde inte startas: {error}")
            return

        self._reset_pending_result()

        self.view.reset_backtest_progress()
        self.view.set_progress_visible(True)
        self.view.set_backtest_running(True)
        self.main_window.set_navigation_enabled(False)

        self.backtest_thread = QThread()

        self.backtest_worker = BacktestWorker(
            season=self.selected_season,
            comparison_type=self.current_comparison_type,
            **worker_settings
        )

        self.backtest_worker.moveToThread(self.backtest_thread)
        self._connect_worker_signals()
        self.backtest_thread.start()

    # --------------------------------------------------
    # Worker-inställningar
    # --------------------------------------------------

    def _create_worker_settings(
        self,
        comparison_type
    ):
        """
            Skapar inställningarna som skickas till BacktestWorker.
        """
        settings = {
            "time_decay": self.OPTIMIZED_TIME_DECAY,
            "history_years": self.OPTIMIZED_HISTORY_YEARS,
            "training_scope": self.OPTIMIZED_TRAINING_SCOPE,
            "time_decay_values": None,
            "history_years_values": None,
            "training_scopes": None,
            "form_match_counts": None,
            "form_weights": None,
            "form_weight": self.OPTIMIZED_FORM_WEIGHT,
            "h2h_match_count": self.H2H_MATCH_COUNT,
            "h2h_weights": None
        }

        if comparison_type == BacktestComparison.TIME_DECAY:
            settings["time_decay_values"] = self._create_time_decay_values()

        elif comparison_type == BacktestComparison.HISTORY_YEARS:
            settings["history_years_values"] = self._create_history_years_values()

        elif comparison_type == BacktestComparison.TRAINING_SCOPE:
            settings["training_scopes"] = self._create_training_scopes()

        elif comparison_type == BacktestComparison.FORM:
            settings["form_match_counts"] = [
                self.OPTIMIZED_FORM_MATCH_COUNT
            ]

            settings["form_weights"] = self._create_form_weights()

        elif comparison_type == BacktestComparison.FORM_MATCH_COUNT:
            settings["form_match_counts"] = self._create_form_match_counts()

        elif comparison_type == BacktestComparison.H2H:
            settings["h2h_weights"] = self._create_h2h_weights()


        elif comparison_type == BacktestComparison.CALIBRATION_MODEL:
            # Kalibreringen ska använda exakt samma
            # formmodell som den ordinarie analysen.
            settings["form_match_counts"] = [
                self.OPTIMIZED_FORM_MATCH_COUNT
            ]

        return settings

    # --------------------------------------------------
    # Intervall
    # --------------------------------------------------

    def _create_time_decay_values(self):
        """
            Skapar time-decay-intervallet från vyn.
        """
        return self._create_decimal_range(
            self.view.get_time_decay_range(),
            step_error=(
                "Time-decay-steget måste vara större än 0."
            ),
            range_error=(
                "Lägsta time decay får inte vara "
                "större än högsta."
            ),
            empty_error=(
                "Intervallet innehåller inga "
                "time-decay-värden."
            )
        )

    def _create_history_years_values(self):
        """
            Skapar intervallet med historiklängder.
        """
        minimum, maximum, step = self.view.get_history_years_range()

        if step <= 0:
            raise ValueError(
                "Steget för historiklängd måste "
                "vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Lägsta historiklängden får inte "
                "vara större än den högsta."
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

    def _create_training_scopes(self):
        """
            Returnerar träningsomfattningarna
            som ska jämföras.
        """
        return [
            TrainingScope.COUNTRY.value,
            TrainingScope.COMPETITION.value
        ]

    def _create_form_match_counts(self):
        """
            Skapar intervallet med antal formmatcher.
        """
        minimum, maximum, step = self.view.get_form_match_count_range()

        if step <= 0:
            raise ValueError(
                "Steget för antal formmatcher måste "
                "vara större än 0."
            )

        if minimum > maximum:
            raise ValueError(
                "Lägsta antalet formmatcher får inte "
                "vara större än det högsta."
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
                "antal formmatcher."
            )

        return values

    def _create_form_weights(self):
        """
            Skapar intervallet med formvikter.
        """
        return self._create_decimal_range(
            self.view.get_form_weight_range(),
            step_error="Formsteget måste vara större än 0.",
            range_error=(
                "Lägsta formvikten får inte vara "
                "större än den högsta."
            ),
            empty_error="Intervallet innehåller inga formvikter."

        )

    def _create_h2h_weights(self):
        """
            Skapar intervallet med H2H-vikter.
        """
        return self._create_decimal_range(
            self.view.get_h2h_weight_range(),
            step_error=(
                "H2H-steget måste vara större än 0."
            ),
            range_error=(
                "Lägsta H2H-vikten får inte vara "
                "större än den högsta."
            ),
            empty_error=(
                "Intervallet innehåller inga H2H-vikter."
            )
        )

    @staticmethod
    def _create_decimal_range(
        value_range,
        *,
        step_error,
        range_error,
        empty_error
    ):
        """
            Skapar ett decimalbaserat flyttalsintervall
            utan ackumulerade flyttalsfel.
        """
        minimum, maximum, step = [
            Decimal(str(value))
            for value in value_range
        ]

        if step <= 0:
            raise ValueError(step_error)

        if minimum > maximum:
            raise ValueError(range_error)

        values = []
        value = minimum

        while value <= maximum:
            values.append(float(value))
            value += step

        if not values:
            raise ValueError(empty_error)

        return values

    # --------------------------------------------------
    # Worker-signaler
    # --------------------------------------------------

    def _connect_worker_signals(self):
        """
            Kopplar worker och QThread.
        """
        self.backtest_thread.started.connect(self.backtest_worker.run)
        self.backtest_worker.progress.connect(self.view.set_backtest_progress)
        self.backtest_worker.finished.connect(self._store_backtest_results)

        self.backtest_worker.cancelled.connect(self._store_backtest_cancelled)
        self.backtest_worker.failed.connect(self._store_backtest_error)
        self.backtest_worker.completed.connect(self.backtest_thread.quit)

        self.backtest_worker.completed.connect(
            self.backtest_worker.deleteLater)
        self.backtest_thread.finished.connect(
            self._on_backtest_thread_finished)

    # --------------------------------------------------
    # Resultat
    # --------------------------------------------------

    def _reset_pending_result(self):
        """
            Nollställer väntande worker-resultat.
        """
        self._pending_results = None
        self._pending_cancelled = False
        self._pending_error = None

    def _store_backtest_results(self, results):
        """
            Sparar resultatet tills worker-tråden har avslutats helt.
        """
        self._pending_results = results

    def _store_backtest_cancelled(self):
        """
            Markerar att körningen avbröts.
        """
        self._pending_cancelled = True

    def _store_backtest_error(self, message):
        """
            Sparar worker-felet tills tråden har avslutats helt.
        """
        self._pending_error = message

    def _on_backtest_thread_finished(self):
        """
            Schemalägger slutlig hantering ett event-loop-varv senare.
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
            Slutför körningen efter att worker-tråden
            har stannat helt.
        """
        if self.backtest_thread is not thread:
            return

        results = self._pending_results
        cancelled = self._pending_cancelled
        error = self._pending_error
        comparison_type = self.current_comparison_type

        self.backtest_worker = None
        self.backtest_thread = None

        self._reset_pending_result()

        thread.deleteLater()

        # Om programmet väntar på att stängas
        # behöver vyn inte uppdateras ytterligare.
        if self._close_when_finished:
            self._close_when_finished = False

            self.main_window.close()
            return

        self.view.set_backtest_running(False)
        self.main_window.set_navigation_enabled(True)
        self._update_run_button()

        if error is not None:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()

            print(
                f"Backtest misslyckades: {error}"
            )

        elif cancelled:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()

        elif results is None:
            self.view.set_progress_visible(False)
            self.view.reset_backtest_progress()

        else:
            self.view.set_backtest_progress(
                100,
                "Klar"
            )

            self.view.show_result(
                results,
                comparison_type
            )

    # --------------------------------------------------
    # Avbryt
    # --------------------------------------------------

    def on_cancel_clicked(self):
        """
            Begär att pågående backtest avbryts.
        """
        self._request_cancel()

    def _request_cancel(self):
        """
            Begär avbrott av pågående backtest.
        """
        if self.backtest_worker is None:
            return

        self.backtest_worker.request_cancel()
        self.view.set_cancel_button_status(False)

    def cancel_and_close(self):
        """
            Avbryter backtestet och stänger programmet
            när worker-tråden har avslutats.
        """
        if self.backtest_thread is None:
            self.main_window.close()
            return

        self._close_when_finished = True

        self._request_cancel()

    # --------------------------------------------------
    # Kopiera
    # --------------------------------------------------

    def on_copy_result_clicked(self):
        """
            Kopierar aktuellt resultat.
        """
        self.view.copy_result()

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def on_back_clicked(self):
        """
            Går tillbaka till backtestinställningarna.
        """
        if self.backtest_thread is not None:
            return

        self.view.show_settings()

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def _update_run_button(self):
        """
            Aktiverar körknappen när en säsong
            är vald och inget backtest pågår.
        """
        enabled = (
            self.selected_season is not None
            and self.backtest_thread is None
        )

        self.view.set_run_button_status(enabled)

    def is_running(self):
        """
            Returnerar True om ett backtest pågår.
        """
        return self.backtest_thread is not None
