from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDateEdit,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class BacktestView(View):
    """
        Vy för att genomföra historiska backtester
        av matchanalysmodellen.

        Vyn består av en inställningssida och
        en separat resultatsida.

        Resultatsidan innehåller en jämförelsesida
        samt en detaljsida med baslinjer och
        kalibrering för det bästa resultatet.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()

    run_clicked = Signal()
    cancel_clicked = Signal()
    copy_result_clicked = Signal()
    back_clicked = Signal()

    # --------------------------------------------------
    # Jämförelsetyper
    # --------------------------------------------------

    COMPARISON_TIME_DECAY = "time_decay"
    COMPARISON_HISTORY_YEARS = "history_years"

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Backtesting"

    GROUP_SETTINGS = "Inställningar"
    GROUP_COMPARISON_TIME_DECAY = "Jämförelse av time decay"
    GROUP_COMPARISON_HISTORY_YEARS = "Jämförelse av historiklängd"
    GROUP_BASELINES = "Baslinjer"
    GROUP_CALIBRATION = "Kalibrering"

    LABEL_COMPETITION = "Tävling"
    LABEL_SEASON = "Säsong"
    LABEL_COMPARISON_TYPE = "Optimera"

    LABEL_START_DATE = "Från datum"
    LABEL_END_DATE = "Till datum"

    LABEL_BEST_TIME_DECAY = "Bästa time decay"
    LABEL_BEST_HISTORY_YEARS = "Bästa historiklängd"

    COMPARISON_NAME_TIME_DECAY = "Time decay"
    COMPARISON_NAME_HISTORY_YEARS = "Historiklängd"

    BUTTON_RUN = "Kör backtest"
    BUTTON_CANCEL = "Avbryt"

    BUTTON_SHOW_DETAILS = "Visa detaljer"
    BUTTON_COPY_RESULT = "Kopiera resultat"
    BUTTON_BACK_TO_COMPARISON = "Tillbaka till jämförelse"

    BUTTON_BACK = "Tillbaka"

    PROGRESS_CALCULATING = "Beräknar återstående tid..."
    EMPTY_VALUE = "-"

    # --------------------------------------------------
    # Jämförelsetabell
    # --------------------------------------------------

    COMPARISON_HEADERS = (
        "Värde",
        "Matcher",
        "Brier score",
        "Log loss",
        "Accuracy"
    )

    COMPARISON_COLUMN_PARAMETER = 0
    COMPARISON_COLUMN_MATCHES = 1
    COMPARISON_COLUMN_BRIER = 2
    COMPARISON_COLUMN_LOG_LOSS = 3
    COMPARISON_COLUMN_ACCURACY = 4

    COMPARISON_COLUMN_COUNT = 5

    # --------------------------------------------------
    # Baslinjetabell
    # --------------------------------------------------

    DETAIL_HEADERS = (
        "Modell",
        "Brier score",
        "Log loss",
        "Accuracy"
    )

    DETAIL_COLUMN_MODEL = 0
    DETAIL_COLUMN_BRIER = 1
    DETAIL_COLUMN_LOG_LOSS = 2
    DETAIL_COLUMN_ACCURACY = 3

    DETAIL_COLUMN_COUNT = 4

    DETAIL_ROW_MODEL = 0
    DETAIL_ROW_UNIFORM = 1
    DETAIL_ROW_HISTORICAL = 2

    DETAIL_ROW_COUNT = 3

    DETAIL_MODEL_NAME = "Dixon-Coles"
    DETAIL_UNIFORM_NAME = "Uniform baslinje"
    DETAIL_HISTORICAL_NAME = "Historisk baslinje"

    # --------------------------------------------------
    # Kalibreringstabell
    # --------------------------------------------------

    CALIBRATION_HEADERS = (
        "Intervall",
        "Modellsnitt",
        "Faktiskt utfall",
        "Observationer"
    )

    CALIBRATION_COLUMN_INTERVAL = 0
    CALIBRATION_COLUMN_MODEL = 1
    CALIBRATION_COLUMN_ACTUAL = 2
    CALIBRATION_COLUMN_OBSERVATIONS = 3

    CALIBRATION_COLUMN_COUNT = 4

    CALIBRATION_ROW_HEIGHT = 28
    CALIBRATION_HEIGHT_MARGIN = 8

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    SECTION_SPACING = 10
    SETTINGS_SPACING = 10

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self):
        """
            Initierar backtestvyn.
        """
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

        self.set_run_button_status(False)
        self.set_cancel_button_status(False)
        self.set_progress_visible(False)

        self.show_settings()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar widgetarnas signaler.
        """
        self.competition_combo.currentIndexChanged.connect(
            lambda _: self.competition_changed.emit()
        )

        self.season_combo.currentIndexChanged.connect(
            lambda _: self.season_changed.emit()
        )

        self.run_button.clicked.connect(
            lambda _: self.run_clicked.emit()
        )

        self.cancel_button.clicked.connect(
            lambda _: self.cancel_clicked.emit()
        )

        self.copy_result_button.clicked.connect(
            lambda _: self.copy_result_clicked.emit()
        )

        self.back_button.clicked.connect(
            lambda _: self.back_clicked.emit()
        )

        self.show_details_button.clicked.connect(
            lambda _: self.show_detail_page()
        )

        self.back_to_comparison_button.clicked.connect(
            lambda _: self.show_comparison_page()
        )

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar samtliga widgetar.
        """
        self._create_selection_widgets()
        self._create_result_widgets()

        self._create_comparison_table()
        self._create_detail_table()
        self._create_calibration_table()

        self.run_button = QPushButton(self.BUTTON_RUN)
        self.cancel_button = QPushButton(self.BUTTON_CANCEL)

        self.show_details_button = QPushButton(self.BUTTON_SHOW_DETAILS)
        self.copy_result_button = QPushButton(self.BUTTON_COPY_RESULT)

        self.back_to_comparison_button = QPushButton(
            self.BUTTON_BACK_TO_COMPARISON
        )

        self.back_button = QPushButton(self.BUTTON_BACK)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")

        self.progress_label = QLabel(self.PROGRESS_CALCULATING)

    def _create_selection_widgets(self):
        """
            Skapar widgetar för backtestinställningarna.
        """
        self.competition_label = QLabel(self.LABEL_COMPETITION)
        self.competition_combo = BaseComboBox()

        self.season_label = QLabel(self.LABEL_SEASON)
        self.season_combo = BaseComboBox()

        self.comparison_type_label = QLabel(self.LABEL_COMPARISON_TYPE)
        self.comparison_type_combo = BaseComboBox()

        self.comparison_type_combo.addItem(
            self.COMPARISON_NAME_TIME_DECAY,
            self.COMPARISON_TIME_DECAY
        )

        self.comparison_type_combo.addItem(
            self.COMPARISON_NAME_HISTORY_YEARS,
            self.COMPARISON_HISTORY_YEARS
        )

        self.start_date_label = QLabel(self.LABEL_START_DATE)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")

        self.end_date_label = QLabel(self.LABEL_END_DATE)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")

    def _create_result_widgets(self):
        """
            Skapar informationen ovanför resultatsidorna.
        """
        self.season_result_label = QLabel()
        self.period_result_label = QLabel()
        self.best_result_label = QLabel()

        self.season_result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.period_result_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.best_result_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

    def _create_comparison_table(self):
        """
            Skapar tabellen för jämförelse
            mellan parametervärden.
        """
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(self.COMPARISON_COLUMN_COUNT)

        self.comparison_table.setHorizontalHeaderLabels(
            self.COMPARISON_HEADERS
        )

        self._configure_table(self.comparison_table)

        self.comparison_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.comparison_table.verticalHeader().setVisible(False)

        header = self.comparison_table.horizontalHeader()

        for column in range(self.COMPARISON_COLUMN_COUNT):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

    def _create_detail_table(self):
        """
            Skapar tabellen för Dixon-Coles och baslinjerna.
        """
        self.detail_table = QTableWidget(
            self.DETAIL_ROW_COUNT,
            self.DETAIL_COLUMN_COUNT
        )

        self.detail_table.setHorizontalHeaderLabels(self.DETAIL_HEADERS)
        self._configure_table(self.detail_table)

        self.detail_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.detail_table.verticalHeader().setVisible(False)

        header = self.detail_table.horizontalHeader()

        for column in range(self.DETAIL_COLUMN_COUNT):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

        self._set_detail_model_names()
        self._adjust_table_height(self.detail_table)

    def _create_calibration_table(self):
        """
            Skapar kalibreringstabellen.
        """
        self.calibration_table = QTableWidget()
        self.calibration_table.setColumnCount(self.CALIBRATION_COLUMN_COUNT)

        self.calibration_table.setHorizontalHeaderLabels(
            self.CALIBRATION_HEADERS
        )

        self._configure_table(self.calibration_table)

        self.calibration_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.calibration_table.verticalHeader().setVisible(False)

        header = self.calibration_table.horizontalHeader()

        for column in range(self.CALIBRATION_COLUMN_COUNT):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

    def _configure_table(self, table):
        """
            Ställer in gemensamma egenskaper
            för resultattabellerna.
        """
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

    # --------------------------------------------------
    # Sidor
    # --------------------------------------------------

    def create_pages(self):
        """
            Skapar inställnings- och resultatsidan.
        """
        self.page_stack = QStackedWidget()

        self.settings_page = self._create_settings_page()
        self.results_page = self._create_results_page()

        self.page_stack.addWidget(self.settings_page)
        self.page_stack.addWidget(self.results_page)

    def _create_settings_page(self):
        """
            Skapar inställningssidan.
        """
        page = QWidget()
        page_layout = QVBoxLayout(page)

        settings_group = QGroupBox(self.GROUP_SETTINGS)
        layout = QGridLayout(settings_group)

        layout.setHorizontalSpacing(self.SETTINGS_SPACING)
        layout.setVerticalSpacing(self.SETTINGS_SPACING)

        layout.addWidget(self.competition_label, 0, 0)
        layout.addWidget(self.competition_combo, 0, 1)

        layout.addWidget(self.season_label, 1, 0)
        layout.addWidget(self.season_combo, 1, 1)

        layout.addWidget(self.comparison_type_label, 2, 0)
        layout.addWidget(self.comparison_type_combo, 2, 1)

        layout.addWidget(self.start_date_label, 3, 0)
        layout.addWidget(self.start_date_edit, 3, 1)

        layout.addWidget(self.end_date_label, 4, 0)
        layout.addWidget(self.end_date_edit, 4, 1)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout, 5, 0, 1, 2)
        layout.addWidget(self.progress_bar, 6, 0, 1, 2)
        layout.addWidget(self.progress_label, 7, 0, 1, 2)

        page_layout.addWidget(settings_group)
        page_layout.addStretch()

        return page

    def _create_results_page(self):
        """
            Skapar resultatsidan.
        """
        page = QWidget()
        page_layout = QVBoxLayout(page)

        information_layout = QHBoxLayout()
        information_layout.setContentsMargins(0, 0, 0, 0)

        information_layout.addWidget(self.season_result_label)
        information_layout.addStretch(1)

        information_layout.addWidget(self.period_result_label)
        information_layout.addStretch(1)

        information_layout.addWidget(self.best_result_label)

        page_layout.addLayout(information_layout)
        page_layout.addSpacing(self.SECTION_SPACING)

        self.result_stack = QStackedWidget()

        self.comparison_page = self._create_comparison_page()
        self.detail_page = self._create_detail_page()

        self.result_stack.addWidget(self.comparison_page)
        self.result_stack.addWidget(self.detail_page)

        page_layout.addWidget(self.result_stack, stretch=1)

        return page

    def _create_comparison_page(self):
        """
            Skapar sidan med parameterjämförelsen.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(0, 0, 0, 0)

        self.comparison_group = QGroupBox(
            self.GROUP_COMPARISON_TIME_DECAY
        )

        comparison_layout = QVBoxLayout(self.comparison_group)

        comparison_layout.addWidget(self.comparison_table)
        layout.addWidget(self.comparison_group, stretch=1)

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.show_details_button)
        button_layout.addWidget(self.copy_result_button)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)

        return page

    def _create_detail_page(self):
        """
            Skapar sidan med baslinjer och
            kalibrering för bästa modell.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(0, 0, 0, 0)

        baseline_group = QGroupBox(self.GROUP_BASELINES)
        baseline_layout = QVBoxLayout(baseline_group)

        baseline_layout.addWidget(self.detail_table)
        layout.addWidget(baseline_group)

        layout.addSpacing(self.SECTION_SPACING)

        calibration_group = QGroupBox(self.GROUP_CALIBRATION)
        calibration_layout = QVBoxLayout(calibration_group)

        calibration_layout.addWidget(self.calibration_table)

        layout.addWidget(calibration_group)
        layout.addStretch()

        layout.addWidget(self.back_to_comparison_button)

        return page

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_settings(self):
        self.page_stack.setCurrentWidget(self.settings_page)

    def show_results(self):
        self.page_stack.setCurrentWidget(self.results_page)

    def show_comparison_page(self):
        self.result_stack.setCurrentWidget(self.comparison_page)

    def show_detail_page(self):
        self.result_stack.setCurrentWidget(self.detail_page)

    # --------------------------------------------------
    # Tävlingar
    # --------------------------------------------------

    def fill_competition_combo(self, competitions):
        self.competition_combo.clear()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.display_name,
                competition
            )

    def get_selected_competition(self):
        return self.competition_combo.currentData()

    # --------------------------------------------------
    # Säsonger
    # --------------------------------------------------

    def fill_season_combo(self, seasons):
        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(
                season.display_name,
                season
            )

    def get_selected_season(self):
        return self.season_combo.currentData()

    # --------------------------------------------------
    # Jämförelsetyp
    # --------------------------------------------------

    def get_selected_comparison_type(self):
        """
            Returnerar vald typ av
            parameterjämförelse.
        """
        return self.comparison_type_combo.currentData()

    # --------------------------------------------------
    # Datum
    # --------------------------------------------------

    def set_date_range(self, start_date, end_date):
        self.start_date_edit.setDate(
            QDate(
                start_date.year,
                start_date.month,
                start_date.day
            )
        )

        self.end_date_edit.setDate(
            QDate(
                end_date.year,
                end_date.month,
                end_date.day
            )
        )

    def get_start_date(self):
        return self.start_date_edit.date().toPython()

    def get_end_date(self):
        return self.end_date_edit.date().toPython()

    # --------------------------------------------------
    # Resultat
    # --------------------------------------------------

    def show_result(
        self,
        results,
        comparison_type
    ):
        """
            Visar resultatet från ett backtest.
        """
        if not results:
            return

        self.current_results = list(results)
        self.current_comparison_type = comparison_type

        season = self.get_selected_season()
        start_date = self.get_start_date()
        end_date = self.get_end_date()

        best_result = min(
            results,
            key=lambda result: (
                result.log_loss,
                result.brier_score
            )
        )

        self.season_result_label.setText(
            season.display_name
            if season is not None
            else self.EMPTY_VALUE
        )

        self.period_result_label.setText(
            f"Period: {start_date:%Y-%m-%d} – {end_date:%Y-%m-%d}"
        )

        self._configure_comparison_result(
            best_result,
            comparison_type
        )

        self.fill_comparison_table(
            results,
            comparison_type
        )

        self.fill_detail_table(best_result)
        self.fill_calibration_table(best_result.calibration_bins)

        self.show_comparison_page()
        self.show_results()

    def _configure_comparison_result(
        self,
        best_result,
        comparison_type
    ):
        """
            Anpassar rubriker och information
            efter vald jämförelsetyp.
        """
        if comparison_type == self.COMPARISON_TIME_DECAY:
            self.comparison_group.setTitle(
                self.GROUP_COMPARISON_TIME_DECAY
            )

            self.comparison_table.setHorizontalHeaderItem(
                self.COMPARISON_COLUMN_PARAMETER,
                QTableWidgetItem("Time decay")
            )

            self.best_result_label.setText(
                f"{self.LABEL_BEST_TIME_DECAY}: "
                f"{best_result.time_decay:.4f}"
            )

            return

        if comparison_type == self.COMPARISON_HISTORY_YEARS:
            self.comparison_group.setTitle(
                self.GROUP_COMPARISON_HISTORY_YEARS
            )

            self.comparison_table.setHorizontalHeaderItem(
                self.COMPARISON_COLUMN_PARAMETER,
                QTableWidgetItem("Historik")
            )

            self.best_result_label.setText(
                f"{self.LABEL_BEST_HISTORY_YEARS}: "
                f"{best_result.history_years} år"
            )

            return

        raise ValueError(
            "Okänd typ av backtestjämförelse."
        )

    def fill_comparison_table(
        self,
        results,
        comparison_type
    ):
        """
            Fyller tabellen med resultaten
            för samtliga parametervärden.
        """
        self.comparison_table.clearContents()
        self.comparison_table.setRowCount(len(results))

        for row, result in enumerate(results):
            parameter_value = self._format_parameter_value(
                result,
                comparison_type
            )

            values = (
                parameter_value,
                str(result.matches_tested),
                f"{result.brier_score:.4f}",
                f"{result.log_loss:.4f}",
                f"{result.accuracy:.1%}"
            )

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.comparison_table.setItem(row, column, item)

    def _format_parameter_value(
        self,
        result,
        comparison_type
    ):
        """
            Formaterar parametervärdet
            för vald jämförelsetyp.
        """
        if comparison_type == self.COMPARISON_TIME_DECAY:
            return f"{result.time_decay:.4f}"

        if comparison_type == self.COMPARISON_HISTORY_YEARS:
            return f"{result.history_years} år"

        raise ValueError(
            "Okänd typ av backtestjämförelse."
        )

    def fill_detail_table(self, result):
        self._set_detail_value(
            self.DETAIL_ROW_MODEL,
            self.DETAIL_COLUMN_BRIER,
            f"{result.brier_score:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_MODEL,
            self.DETAIL_COLUMN_LOG_LOSS,
            f"{result.log_loss:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_MODEL,
            self.DETAIL_COLUMN_ACCURACY,
            f"{result.accuracy:.1%}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_UNIFORM,
            self.DETAIL_COLUMN_BRIER,
            f"{result.uniform_brier_score:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_UNIFORM,
            self.DETAIL_COLUMN_LOG_LOSS,
            f"{result.uniform_log_loss:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_UNIFORM,
            self.DETAIL_COLUMN_ACCURACY,
            self.EMPTY_VALUE
        )

        self._set_detail_value(
            self.DETAIL_ROW_HISTORICAL,
            self.DETAIL_COLUMN_BRIER,
            f"{result.historical_brier_score:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_HISTORICAL,
            self.DETAIL_COLUMN_LOG_LOSS,
            f"{result.historical_log_loss:.4f}"
        )

        self._set_detail_value(
            self.DETAIL_ROW_HISTORICAL,
            self.DETAIL_COLUMN_ACCURACY,
            self.EMPTY_VALUE
        )

    def _set_detail_model_names(self):
        names = (
            self.DETAIL_MODEL_NAME,
            self.DETAIL_UNIFORM_NAME,
            self.DETAIL_HISTORICAL_NAME
        )

        for row, name in enumerate(names):
            self._set_detail_value(row, self.DETAIL_COLUMN_MODEL, name)

    def _set_detail_value(self, row, column, value):
        item = QTableWidgetItem(str(value))

        if column == self.DETAIL_COLUMN_MODEL:
            alignment = (
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignVCenter
            )
        else:
            alignment = Qt.AlignmentFlag.AlignCenter

        item.setTextAlignment(alignment)
        self.detail_table.setItem(row, column, item)

    # --------------------------------------------------
    # Kopiering
    # --------------------------------------------------

    def copy_result(self):
        """
            Kopierar det visade backtestresultatet
            till urklipp med hög precision.
        """
        if not self.current_results:
            return

        if self.current_comparison_type is None:
            return

        lines = [
            self.season_result_label.text(),
            self.period_result_label.text(),
            self.best_result_label.text(),
            ""
        ]

        if (
            self.current_comparison_type
            == self.COMPARISON_TIME_DECAY
        ):
            parameter_header = "Time decay"

        elif (
            self.current_comparison_type
            == self.COMPARISON_HISTORY_YEARS
        ):
            parameter_header = "Historik"

        else:
            return

        headers = (
            parameter_header,
            "Matcher",
            "Brier score",
            "Log loss",
            "Accuracy"
        )

        lines.append("\t".join(headers))

        for result in self.current_results:
            parameter_value = self._format_parameter_value(
                result,
                self.current_comparison_type
            )

            values = (
                parameter_value,
                str(result.matches_tested),
                f"{result.brier_score:.8f}",
                f"{result.log_loss:.8f}",
                f"{result.accuracy:.1%}"
            )

            lines.append("\t".join(values))

        QApplication.clipboard().setText("\n".join(lines))

    # --------------------------------------------------
    # Kalibrering
    # --------------------------------------------------

    def fill_calibration_table(self, calibration_bins):
        """
            Fyller kalibreringstabellen.
        """
        self.calibration_table.clearContents()
        self.calibration_table.setRowCount(len(calibration_bins))

        for row, calibration_bin in enumerate(calibration_bins):
            values = (
                (
                    f"{calibration_bin.lower_bound:.0%}"
                    " – "
                    f"{calibration_bin.upper_bound:.0%}"
                ),
                f"{calibration_bin.average_probability:.1%}",
                f"{calibration_bin.actual_frequency:.1%}",
                str(calibration_bin.observations)
            )

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.calibration_table.setItem(row, column, item)

            self.calibration_table.setRowHeight(
                row,
                self.CALIBRATION_ROW_HEIGHT
            )

        self._adjust_calibration_table_height()

    # --------------------------------------------------
    # Tabellstorlek
    # --------------------------------------------------

    def _adjust_table_height(self, table):
        """
            Anpassar en mindre tabells höjd
            efter dess innehåll.
        """
        table.resizeRowsToContents()

        height = table.horizontalHeader().height()

        for row in range(table.rowCount()):
            height += table.rowHeight(row)

        height += table.frameWidth() * 2

        table.setFixedHeight(height)

    def _adjust_calibration_table_height(self):
        """
            Anpassar kalibreringstabellens höjd
            efter antalet rader.
        """
        height = self.calibration_table.horizontalHeader().height()

        height += (
            self.calibration_table.rowCount()
            * self.CALIBRATION_ROW_HEIGHT
        )

        height += self.calibration_table.frameWidth() * 2
        height += self.CALIBRATION_HEIGHT_MARGIN

        self.calibration_table.setFixedHeight(height)

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def set_backtest_progress(self, percent, remaining_text):
        """
            Uppdaterar progressbaren och texten
            för återstående tid.
        """
        self.progress_bar.setValue(percent)
        self.progress_label.setText(remaining_text)

    def reset_backtest_progress(self):
        """
            Återställer progressinformationen.
        """
        self.progress_bar.setValue(0)
        self.progress_label.setText(self.PROGRESS_CALCULATING)

    def set_progress_visible(self, visible):
        """
            Visar eller döljer
            progressinformationen.
        """
        self.progress_bar.setVisible(visible)
        self.progress_label.setVisible(visible)

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_result(self):
        """
            Tömmer tidigare backtestresultat.
        """
        self.current_results = []
        self.current_comparison_type = None

        self.season_result_label.setText(self.EMPTY_VALUE)
        self.period_result_label.setText(self.EMPTY_VALUE)
        self.best_result_label.setText(self.EMPTY_VALUE)

        self.comparison_table.clearContents()
        self.comparison_table.setRowCount(0)

        for row in range(self.DETAIL_ROW_COUNT):
            for column in (
                self.DETAIL_COLUMN_BRIER,
                self.DETAIL_COLUMN_LOG_LOSS,
                self.DETAIL_COLUMN_ACCURACY
            ):
                self._set_detail_value(row, column, self.EMPTY_VALUE)

        self.calibration_table.clearContents()
        self.calibration_table.setRowCount(0)

    def set_run_button_status(self, status):
        """
            Aktiverar eller inaktiverar
            backtestknappen.
        """
        self.run_button.setEnabled(status)

    def set_cancel_button_status(self, status):
        """
            Aktiverar eller inaktiverar
            avbrytknappen.
        """
        self.cancel_button.setEnabled(status)

    def set_backtest_running(self, running):
        """
            Uppdaterar vyn beroende på
            om ett backtest pågår.
        """
        self.cancel_button.setEnabled(running)

        self.competition_combo.setEnabled(not running)
        self.season_combo.setEnabled(not running)
        self.comparison_type_combo.setEnabled(not running)

        self.start_date_edit.setEnabled(not running)
        self.end_date_edit.setEnabled(not running)

        if running:
            self.run_button.setEnabled(False)
