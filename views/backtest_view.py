from mvc import View
from models.backtest.backtest_types import BacktestComparison, TrainingScope
from misc.combo_boxes.base_combo_box import BaseComboBox
from misc.buttons import BackButton, CancelButton, CopyButton, RunBacktestButton
from misc.base_table_widget import BaseTableWidget
from PySide6.QtWidgets import QGroupBox, QLabel, QProgressBar, QStackedWidget, QTableWidgetItem, QWidget
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, Signal
from widgets.range_settings_widget import RangeConfig, RangeSettingsWidget


class BacktestView(View):
    """
        Vy för att genomföra historiska backtester av matchanalysmodellen.

        Vyn kan jämföra time decay, historiklängd, omfattning av träningsdata
        och form samt genomföra rho-diagnostik.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()
    run_clicked = Signal()
    back_clicked = Signal()
    cancel_clicked = Signal()
    copy_result_clicked = Signal()

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Backtesting"
    GROUP_SETTINGS = "Inställningar"
    GROUP_RESULTS = "Resultat"

    LABEL_COMPETITION = "Tävling"
    LABEL_SEASON = "Säsong"
    LABEL_COMPARISON = "Optimera"

    EMPTY_VALUE = "-"

    # Kompatibilitetskonstanter som används av BacktestController.
    COMPARISON_TIME_DECAY = BacktestComparison.TIME_DECAY.value
    COMPARISON_HISTORY_YEARS = BacktestComparison.HISTORY_YEARS.value
    COMPARISON_TRAINING_SCOPE = BacktestComparison.TRAINING_SCOPE.value
    COMPARISON_FORM = BacktestComparison.FORM.value
    COMPARISON_FORM_MATCH_COUNT = BacktestComparison.FORM_MATCH_COUNT.value
    COMPARISON_H2H = BacktestComparison.H2H.value
    COMPARISON_WORKER_BENCHMARK = BacktestComparison.WORKER_BENCHMARK.value
    COMPARISON_RHO_DIAGNOSTICS = BacktestComparison.RHO_DIAGNOSTICS.value
    COMPARISON_RHO_COMPARISON = BacktestComparison.RHO_COMPARISON.value

    RESULT_COLUMN_PARAMETER = 0

    RESULT_HEADERS = ("Värde", "Matcher", "Brier score",
                      "Log loss", "Accuracy")
    RHO_RESULT_HEADERS = ("Mått", "Värde")
    WORKER_RESULT_HEADERS = ("Workers", "Körningar",
                             "Median", "Snabbast", "Långsammast")

    # --------------------------------------------------
    # Jämförelser
    # --------------------------------------------------

    TRAINING_SCOPE_LABELS = {
        TrainingScope.COUNTRY.value: "Hela landet",
        TrainingScope.COMPETITION.value: "Endast tävlingen"
    }

    # --------------------------------------------------
    # Intervall
    # --------------------------------------------------

    TIME_DECAY_RANGE = RangeConfig(
        minimum_label="Time-decay från",
        maximum_label="Time-decay till",
        step_label="Time-decay-steg",
        minimum=0.0000,
        maximum=0.1000,
        default_minimum=0.0010,
        default_maximum=0.0100,
        default_step=0.0010,
        decimals=4,
        single_step=0.0010
    )

    HISTORY_RANGE = RangeConfig(
        minimum_label="Historik från",
        maximum_label="Historik till",
        step_label="Historiksteg",
        minimum=1,
        maximum=10,
        default_minimum=1,
        default_maximum=5,
        default_step=1,
        integer=True
    )

    FORM_MATCH_COUNT_RANGE = RangeConfig(
        minimum_label="Formmatcher från",
        maximum_label="Formmatcher till",
        step_label="Formmatcher steg",
        minimum=1,
        maximum=20,
        default_minimum=3,
        default_maximum=10,
        default_step=1,
        integer=True
    )

    FORM_RANGE = RangeConfig(
        minimum_label="Formvikt från",
        maximum_label="Formvikt till",
        step_label="Formvikt-steg",
        minimum=0.00,
        maximum=2.00,
        default_minimum=0.00,
        default_maximum=0.10,
        default_step=0.02,
        decimals=2,
        single_step=0.01
    )

    H2H_RANGE = RangeConfig(
        minimum_label="H2H-vikt från",
        maximum_label="H2H-vikt till",
        step_label="H2H-vikt steg",
        minimum=0.00,
        maximum=2.00,
        default_minimum=0.00,
        default_maximum=0.20,
        default_step=0.01,
        decimals=2,
        single_step=0.01
    )

    # --------------------------------------------------
    # Jämförelsekonfiguration
    # --------------------------------------------------

    COMPARISON_CONFIG = {
        BacktestComparison.TIME_DECAY.value: {
            "label": "Time-decay",
            "header": "Time-decay",
            "best_label": "Bästa time-decay",
            "range": TIME_DECAY_RANGE,
            "format": lambda result: f"{result.time_decay:.4f}"
        },
        BacktestComparison.HISTORY_YEARS.value: {
            "label": "Historiklängd",
            "header": "Historik",
            "best_label": "Bästa historiklängd",
            "range": HISTORY_RANGE,
            "format": lambda result: f"{result.history_years} år"
        },
        BacktestComparison.TRAINING_SCOPE.value: {
            "label": "Träningsdata",
            "header": "Träningsdata",
            "best_label": "Bästa träningsdata"
        },
        BacktestComparison.FORM.value: {
            "label": "Form",
            "header": "Formvikt",
            "best_label": "Bästa formvikt",
            "range": FORM_RANGE,
            "format": lambda result: f"{result.form_weight:.2f}"
        },
        BacktestComparison.FORM_MATCH_COUNT.value: {
            "label": "Antal formmatcher",
            "header": "Formmatcher",
            "best_label": "Bästa antal formmatcher",
            "range": FORM_MATCH_COUNT_RANGE,
            "format": lambda result: str(result.form_match_count)
        },
        BacktestComparison.H2H.value: {
            "label": "Inbördes möten",
            "header": "H2H-vikt",
            "best_label": "Bästa H2H-vikt",
            "range": H2H_RANGE,
            "format": lambda result: f"{result.h2h_weight:.2f}"
        },
        BacktestComparison.WORKER_BENCHMARK.value: {
            "label": "Worker-benchmark",
            "header": "Workers"
        },
        BacktestComparison.RHO_DIAGNOSTICS.value: {
            "label": "Rho-diagnostik"
        },
        BacktestComparison.RHO_COMPARISON.value: {
            "label": "Rho-jämförelse",
            "header": "Rho",
            "best_label": "Bästa rho-modell",
            "format": lambda result: result.rho_label
        }
    }

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    SECTION_SPACING = 12
    SETTINGS_SPACING = 10
    MARGIN = 12

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self):
        """Initierar backtestvyn."""
        super().__init__()

        self.current_results = []
        self.current_comparison_type = None

        self.layout = self.create_main_layout()
        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.create_widgets()
        self.create_pages()
        self.layout.addWidget(self.page_stack, stretch=1)
        self.setLayout(self.layout)

        self._setup_signals()
        self.clear_result()
        self.reset_backtest_progress()
        self.set_progress_visible(False)
        self.set_run_button_status(False)
        self._update_comparison_settings_visibility()
        self.show_settings()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """Kopplar widgetarnas signaler till vyklassens egna signaler."""
        self.competition_combo.currentIndexChanged.connect(
            lambda _: self.competition_changed.emit())
        self.season_combo.currentIndexChanged.connect(
            lambda _: self.season_changed.emit())
        self.comparison_combo.currentIndexChanged.connect(
            lambda _: self._update_comparison_settings_visibility())

        self.run_button.clicked.connect(self.run_clicked.emit)
        self.back_button.clicked.connect(self.back_clicked.emit)
        self.cancel_button.clicked.connect(self.cancel_clicked.emit)
        self.copy_result_button.clicked.connect(self.copy_result_clicked.emit)

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """Skapar samtliga widgetar i vyn."""
        self._create_selection_widgets()
        self._create_range_widgets()
        self._create_progress_widgets()
        self._create_result_widgets()
        self._create_buttons()

    def _create_selection_widgets(self):
        """Skapar val för tävling, säsong och jämförelsetyp."""
        self.competition_label = QLabel(self.LABEL_COMPETITION)
        self.competition_combo = BaseComboBox()
        self.season_label = QLabel(self.LABEL_SEASON)
        self.season_combo = BaseComboBox()
        self.comparison_label = QLabel(self.LABEL_COMPARISON)
        self.comparison_combo = BaseComboBox()

        for value, config in self.COMPARISON_CONFIG.items():
            self.comparison_combo.addItem(config["label"], value)

    def _create_range_widgets(self):
        """Skapar intervallwidgetar för jämförelser som använder intervall."""
        self.range_settings = {
            comparison_type: RangeSettingsWidget(config["range"])
            for comparison_type, config in self.COMPARISON_CONFIG.items()
            if "range" in config
        }

    def _create_progress_widgets(self):
        """Skapar widgetar för backtestets förlopp."""
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _create_result_widgets(self):
        """Skapar widgetar för resultatvisningen."""
        self.season_result_label = QLabel()
        self.best_result_label = QLabel()

        alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self.season_result_label.setAlignment(alignment)
        self.best_result_label.setAlignment(alignment)

        self.result_table = BaseTableWidget(
            readonly=True, selection=False, headers=self.RESULT_HEADERS)
        self.result_table.verticalHeader().setVisible(False)

    def _create_buttons(self):
        """Skapar vyklassens knappar."""
        self.run_button = RunBacktestButton()
        self.back_button = BackButton()
        self.cancel_button = CancelButton()
        self.copy_result_button = CopyButton()

        self.cancel_button.setEnabled(False)
        self.copy_result_button.setEnabled(False)

    # --------------------------------------------------
    # Intervall
    # --------------------------------------------------

    def get_range(self, comparison_type):
        """Returnerar valt intervall för angiven jämförelsetyp."""
        widget = self.range_settings.get(comparison_type)
        return widget.get_range() if widget is not None else None

    def get_time_decay_range(self):
        """Returnerar valt intervall för time decay."""
        return self.get_range(BacktestComparison.TIME_DECAY.value)

    def get_history_years_range(self):
        """Returnerar valt intervall för historiklängd."""
        return self.get_range(BacktestComparison.HISTORY_YEARS.value)

    def get_form_weight_range(self):
        """Returnerar valt intervall för formvikt."""
        return self.get_range(BacktestComparison.FORM.value)

    def get_form_match_count_range(self):
        """Returnerar valt intervall för antal formmatcher."""
        return self.get_range(BacktestComparison.FORM_MATCH_COUNT.value)

    def get_h2h_weight_range(self):
        """Returnerar valt intervall för H2H-vikt."""
        return self.get_range(BacktestComparison.H2H.value)

    # --------------------------------------------------
    # Sidor
    # --------------------------------------------------

    def create_pages(self):
        """Skapar inställnings- och resultatsidan."""
        self.page_stack = QStackedWidget()
        self.settings_page = self._create_settings_page()
        self.results_page = self._create_results_page()

        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.results_page)

    def _create_settings_page(self):
        """Skapar sidan med backtestinställningar."""
        page = QWidget()
        page_layout = self.create_vertical_layout(page)

        settings_group = QGroupBox(self.GROUP_SETTINGS)
        layout = self.create_grid_layout(
            parent=settings_group,
            margin=self.MARGIN,
            horizontal_spacing=self.SETTINGS_SPACING,
            vertical_spacing=self.SETTINGS_SPACING
        )

        selections = (
            (self.competition_label, self.competition_combo),
            (self.season_label, self.season_combo),
            (self.comparison_label, self.comparison_combo)
        )

        for row, (label, combo) in enumerate(selections):
            layout.addWidget(label, row, 0)
            layout.addWidget(combo, row, 1)

        for widget in self.range_settings.values():
            layout.addWidget(widget, 3, 0, 1, 2)

        button_layout = self.create_horizontal_layout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout, 6, 0, 1, 2)

        progress_layout = self.create_vertical_layout()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout, 7, 0, 1, 2)

        page_layout.addWidget(settings_group)
        page_layout.addStretch()

        return page

    def _create_results_page(self):
        """Skapar sidan för backtestresultat."""
        page = QWidget()
        page_layout = self.create_vertical_layout(page)

        information_layout = self.create_grid_layout()
        information_layout.addWidget(self.season_result_label, 0, 0)
        information_layout.addWidget(self.best_result_label, 1, 0)
        information_layout.setColumnStretch(0, 1)

        page_layout.addLayout(information_layout)
        page_layout.addSpacing(self.SECTION_SPACING)
        page_layout.addWidget(QLabel(self.GROUP_RESULTS))
        page_layout.addWidget(self.result_table, stretch=1)

        button_layout = self.create_horizontal_layout()
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.copy_result_button)
        page_layout.addLayout(button_layout)

        return page

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_settings(self):
        """Visar inställningssidan."""
        self.page_stack.setCurrentWidget(self.settings_page)

    def show_results(self):
        """Visar resultatsidan."""
        self.page_stack.setCurrentWidget(self.results_page)

    # --------------------------------------------------
    # Val
    # --------------------------------------------------

    def _fill_combo(self, combo, items, changed_signal):
        """Fyller en combo box och signalerar när första valet har satts."""
        combo.blockSignals(True)
        combo.clear()

        for item in items:
            combo.addItem(item.display_name, item)

        combo.blockSignals(False)

        if combo.count():
            combo.setCurrentIndex(0)
            changed_signal.emit()

    def fill_competition_combo(self, competitions):
        """Fyller listan med tillgängliga tävlingar."""
        self._fill_combo(self.competition_combo, competitions,
                         self.competition_changed)

    def fill_season_combo(self, seasons):
        """Fyller listan med tillgängliga säsonger."""
        self._fill_combo(self.season_combo, seasons, self.season_changed)

    def get_selected_competition(self):
        """Returnerar vald tävling."""
        return self.competition_combo.currentData()

    def get_selected_season(self):
        """Returnerar vald säsong."""
        return self.season_combo.currentData()

    def get_selected_comparison_type(self):
        """Returnerar vald jämförelsetyp."""
        return self.comparison_combo.currentData()

    def _update_comparison_settings_visibility(self):
        """Visar endast intervallinställningen för vald jämförelsetyp."""
        comparison_type = self.get_selected_comparison_type()

        for value, widget in self.range_settings.items():
            widget.setVisible(value == comparison_type)

    # --------------------------------------------------
    # Resultat
    # --------------------------------------------------

    def show_result(self, results, comparison_type):
        """Visar resultat för genomfört backtest."""
        if not results:
            return

        self.current_comparison_type = comparison_type
        self.season_result_label.setText(
            self._get_season_result_text(results, comparison_type))

        if comparison_type == BacktestComparison.RHO_DIAGNOSTICS.value:
            self.current_results = results
            self._show_rho_result(results)
        else:
            self.current_results = list(results)
            self._configure_result_table_for_comparison(comparison_type)
            self.fill_result_table(results, comparison_type)

            best_result = self._get_best_result(results, comparison_type)
            self.best_result_label.setText(
                self._get_best_result_text(best_result, comparison_type))

        self.copy_result_button.setEnabled(True)
        self.show_results()

    def _get_season_result_text(self, results, comparison_type):
        """Skapar text för resultatets säsong och eventuell H2H-information."""
        season = self.get_selected_season()
        text = season.display_name if season is not None else self.EMPTY_VALUE

        if comparison_type != BacktestComparison.H2H.value:
            return text

        result = results[0]
        eligible = getattr(result, "h2h_eligible_matches", None)
        excluded = getattr(result, "h2h_excluded_matches", None)
        required = getattr(result, "h2h_required_matches", None)

        if None in (eligible, excluded, required):
            return text

        return f"{text} | Minst {required} H2H: {eligible} inkluderade, {excluded} exkluderade"

    def _show_rho_result(self, result):
        """Visar resultat från rho-diagnostiken."""
        self._configure_result_table_for_comparison(
            BacktestComparison.RHO_DIAGNOSTICS.value)
        self.best_result_label.setText("Rho-diagnostik")
        self._fill_result_rows(self._get_rho_result_rows(result))

    def _get_rho_result_rows(self, result):
        """Skapar tabellrader för rho-diagnostiken."""
        return (
            ("Matcher", result["match_count"]),
            ("Unika matchdatum", result["match_date_count"]),
            ("Rho-skattningar", result["count"]),
            ("Unika rho-referensdatum", result["reference_date_count"]),
            ("Duplicerade rho-datum",
             result["duplicate_reference_date_count"]),
            ("Saknade matchdatum", result["missing_reference_date_count"]),
            ("Extra rho-datum", result["extra_reference_date_count"]),
            ("Minimum", f'{result["minimum"]:.6f}'),
            ("5:e percentilen", f'{result["percentile_05"]:.6f}'),
            ("Medel", f'{result["mean"]:.6f}'),
            ("Median", f'{result["median"]:.6f}'),
            ("95:e percentilen", f'{result["percentile_95"]:.6f}'),
            ("Maximum", f'{result["maximum"]:.6f}'),
            ("Nedre bound", f'{result["lower_bound"]:.6f}'),
            ("Övre bound", f'{result["upper_bound"]:.6f}'),
            ("Nära nedre bound",
             f'{result["lower_bound_count"]} ({result["lower_bound_percentage"]:.1f} %)'),
            ("Nära övre bound",
             f'{result["upper_bound_count"]} ({result["upper_bound_percentage"]:.1f} %)')
        )

    def _configure_result_table_for_comparison(self, comparison_type):
        """Anpassar resultattabellen efter vald jämförelsetyp."""
        if comparison_type == BacktestComparison.RHO_DIAGNOSTICS.value:
            headers = self.RHO_RESULT_HEADERS
        elif comparison_type == BacktestComparison.WORKER_BENCHMARK.value:
            headers = self.WORKER_RESULT_HEADERS
        else:
            headers = list(self.RESULT_HEADERS)
            headers[self.RESULT_COLUMN_PARAMETER] = self._get_parameter_header(
                comparison_type)

        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        self.result_table.set_wide_columns()

    def fill_result_table(self, results, comparison_type):
        """Fyller resultattabellen med backtestresultat."""
        rows = [self._get_result_values(
            result, comparison_type) for result in results]
        self._fill_result_rows(rows)

    def _fill_result_rows(self, rows):
        """Skriver givna rader till resultattabellen."""
        self.result_table.clearContents()
        self.result_table.setRowCount(len(rows))

        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.result_table.setItem(row, column, item)

        self.result_table.resizeRowsToContents()

    def _get_result_values(self, result, comparison_type):
        """Formaterar en resultatrad för vald jämförelsetyp."""
        if comparison_type == BacktestComparison.WORKER_BENCHMARK.value:
            return (
                str(result.worker_count),
                str(result.run_count),
                f"{result.median_seconds:.2f} s",
                f"{result.minimum_seconds:.2f} s",
                f"{result.maximum_seconds:.2f} s"
            )

        return (
            self._format_parameter_value(result, comparison_type),
            str(result.matches_tested),
            f"{result.brier_score:.8f}",
            f"{result.log_loss:.8f}",
            f"{result.accuracy:.1%}"
        )

    def _format_parameter_value(self, result, comparison_type):
        """Formaterar parametervärdet för visning."""
        if comparison_type == BacktestComparison.TRAINING_SCOPE.value:
            return self.TRAINING_SCOPE_LABELS.get(result.training_scope, result.training_scope)

        formatter = self.COMPARISON_CONFIG.get(
            comparison_type, {}).get("format")
        return formatter(result) if formatter else self.EMPTY_VALUE

    def _get_best_result(self, results, comparison_type):
        """Returnerar det bästa resultatet för vald jämförelsetyp."""
        if comparison_type == BacktestComparison.WORKER_BENCHMARK.value:
            return min(results, key=lambda result: result.median_seconds)

        return min(results, key=lambda result: (result.log_loss, result.brier_score))

    def _get_best_result_text(self, result, comparison_type):
        """Skapar sammanfattningstext för bästa resultat."""
        if comparison_type == BacktestComparison.WORKER_BENCHMARK.value:
            return f"Snabbast: {result.worker_count} workers, {result.median_seconds:.2f} s"

        config = self.COMPARISON_CONFIG.get(comparison_type, {})
        label = config.get("best_label")

        if label is None:
            return self.EMPTY_VALUE

        return f"{label}: {self._format_parameter_value(result, comparison_type)}"

    def _get_parameter_header(self, comparison_type):
        """Returnerar rubriken för parameterkolumnen."""
        return self.COMPARISON_CONFIG.get(comparison_type, {}).get("header", "Värde")

    # --------------------------------------------------
    # Kopiering
    # --------------------------------------------------

    def copy_result(self):
        """Kopierar aktuellt resultat till urklipp."""
        if not self.current_results or self.current_comparison_type is None:
            return

        season = self.get_selected_season()
        title = season.display_name if season is not None else self.EMPTY_VALUE
        comparison_type = self.current_comparison_type

        if comparison_type == BacktestComparison.RHO_DIAGNOSTICS.value:
            self._copy_rho_result(title)
            return

        best_result = self._get_best_result(
            self.current_results, comparison_type)

        if comparison_type == BacktestComparison.WORKER_BENCHMARK.value:
            headers = self.WORKER_RESULT_HEADERS
        else:
            headers = (
                self._get_parameter_header(comparison_type),
                "Matcher",
                "Brier score",
                "Log loss",
                "Accuracy"
            )

        lines = [
            title,
            self._get_best_result_text(best_result, comparison_type),
            "",
            "\t".join(headers)
        ]

        for result in self.current_results:
            lines.append(
                "\t".join(self._get_result_values(result, comparison_type)))

        QGuiApplication.clipboard().setText("\n".join(lines))

    def _copy_rho_result(self, title):
        """Kopierar rho-diagnostiken till urklipp."""
        result = self.current_results
        lines = [title, "Rho-diagnostik", "",
                 "\t".join(self.RHO_RESULT_HEADERS)]

        for measure, value in self._get_rho_result_rows(result):
            lines.append(f"{measure}\t{value}")

        if result["missing_reference_dates"]:
            lines.extend(["", "Saknade matchdatum:", *
                         map(str, result["missing_reference_dates"])])

        if result["extra_reference_dates"]:
            lines.extend(["", "Extra rho-datum:", *
                         map(str, result["extra_reference_dates"])])

        QGuiApplication.clipboard().setText("\n".join(lines))

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def set_backtest_progress(self, value, text):
        """Uppdaterar backtestets progress och text."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)

    def reset_backtest_progress(self):
        """Återställer backtestets progress."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("")

    def set_progress_visible(self, visible):
        """Visar eller döljer progressinformationen."""
        self.progress_bar.setVisible(visible)
        self.progress_label.setVisible(visible)

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_result(self):
        """Rensar tidigare backtestresultat."""
        self.current_results = []
        self.current_comparison_type = None

        self.season_result_label.setText(self.EMPTY_VALUE)
        self.best_result_label.setText(self.EMPTY_VALUE)

        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.copy_result_button.setEnabled(False)

    def set_run_button_status(self, status):
        """Aktiverar eller inaktiverar körknappen."""
        self.run_button.setEnabled(status)

    def set_cancel_button_status(self, status):
        """Aktiverar eller inaktiverar avbrytknappen."""
        self.cancel_button.setEnabled(status)

    def set_backtest_running(self, running):
        """Anpassar vykomponenterna efter om ett backtest körs."""
        enabled = not running

        self.run_button.setEnabled(enabled)
        self.cancel_button.setEnabled(running)

        self.competition_combo.setEnabled(enabled)
        self.season_combo.setEnabled(enabled)
        self.comparison_combo.setEnabled(enabled)

        for widget in self.range_settings.values():
            widget.set_enabled(enabled)
