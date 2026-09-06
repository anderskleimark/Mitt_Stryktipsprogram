from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QAbstractItemView, QGroupBox, QHeaderView,
                               QLabel, QProgressBar, QStackedWidget,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (BackButton, CancelButton, CopyButton,
                          RunBacktestButton)
from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class BacktestView(View):
    """
        Vy för att genomföra historiska backtester
        av matchanalysmodellen.

        Vyn kan jämföra time decay, historiklängd
        och omfattning av träningsdata.
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
    # Jämförelsetyper
    # --------------------------------------------------

    COMPARISON_TIME_DECAY = "time_decay"
    COMPARISON_HISTORY_YEARS = "history_years"
    COMPARISON_TRAINING_SCOPE = "training_scope"

    # --------------------------------------------------
    # Träningsdata
    # --------------------------------------------------

    TRAINING_SCOPE_COUNTRY = "country"
    TRAINING_SCOPE_COMPETITION = "competition"

    TRAINING_SCOPE_LABELS = {
        TRAINING_SCOPE_COUNTRY: "Hela landet",
        TRAINING_SCOPE_COMPETITION: "Endast tävlingen"
    }

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Backtesting"

    GROUP_SETTINGS = "Inställningar"
    GROUP_RESULTS = "Resultat"

    LABEL_COMPETITION = "Tävling"
    LABEL_SEASON = "Säsong"
    LABEL_COMPARISON = "Optimera"

    EMPTY_VALUE = "–"

    # --------------------------------------------------
    # Resultattabell
    # --------------------------------------------------

    RESULT_COLUMN_PARAMETER = 0
    RESULT_COLUMN_MATCHES = 1
    RESULT_COLUMN_BRIER = 2
    RESULT_COLUMN_LOG_LOSS = 3
    RESULT_COLUMN_ACCURACY = 4

    RESULT_COLUMN_COUNT = 5

    RESULT_HEADERS = (
        "Värde",
        "Matcher",
        "Brier score",
        "Log loss",
        "Accuracy"
    )

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
        """
            Initierar backtestvyn.
        """
        super().__init__()

        # Etiketter
        self.competition_label = None
        self.season_label = None
        self.comparison_label = None
        self.progress_label = None
        self.season_result_label = None
        self.best_result_label = None

        # Combo-boxar
        self.competition_combo = None
        self.season_combo = None
        self.comparison_combo = None

        # Progressbar och tabell
        self.progress_bar = None
        self.result_table = None

        self.current_results = []
        self.current_comparison_type = None

        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.create_widgets()
        self.create_pages()

        self.layout.addWidget(
            self.page_stack,
            stretch=1
        )

        self.setLayout(self.layout)

        self._setup_signals()

        self.clear_result()
        self.reset_backtest_progress()
        self.set_progress_visible(False)
        self.set_run_button_status(False)

        self.show_settings()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar widgetarnas signaler till vyklassens egna signaler.
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

        self.back_button.clicked.connect(
            lambda _: self.back_clicked.emit()
        )

        self.cancel_button.clicked.connect(
            lambda _: self.cancel_clicked.emit()
        )

        self.copy_result_button.clicked.connect(
            lambda _: self.copy_result_clicked.emit()
        )

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar samtliga widgetar.
        """
        self._create_selection_widgets()
        self._create_progress_widgets()
        self._create_result_widgets()

        self.run_button = RunBacktestButton()
        self.back_button = BackButton()
        self.cancel_button = CancelButton()
        self.copy_result_button = CopyButton()

        self.cancel_button.setEnabled(False)
        self.copy_result_button.setEnabled(False)

    def _create_selection_widgets(self):
        """
            Skapar widgetar för backtestinställningarna.
        """
        self.competition_label = QLabel(self.LABEL_COMPETITION)
        self.competition_combo = BaseComboBox()

        self.season_label = QLabel(self.LABEL_SEASON)
        self.season_combo = BaseComboBox()

        self.comparison_label = QLabel(self.LABEL_COMPARISON)
        self.comparison_combo = BaseComboBox()

        self.comparison_combo.addItem(
            "Time decay",
            self.COMPARISON_TIME_DECAY
        )

        self.comparison_combo.addItem(
            "Historiklängd",
            self.COMPARISON_HISTORY_YEARS
        )

        self.comparison_combo.addItem(
            "Träningsdata",
            self.COMPARISON_TRAINING_SCOPE
        )

    def _create_progress_widgets(self):
        """
            Skapar widgetar för backtestets förlopp.
        """
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _create_result_widgets(self):
        """
            Skapar resultatöversikten.
        """
        self.season_result_label = QLabel()
        self.best_result_label = QLabel()

        self.season_result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.best_result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.result_table = BaseTableWidget(headers=self.RESULT_HEADERS)

        self._configure_table(self.result_table)

        self.result_table.verticalHeader().setVisible(False)

        header = self.result_table.horizontalHeader()

        for column in range(self.RESULT_COLUMN_COUNT):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

    def _configure_table(self, table):
        """
            Ställer in gemensamma egenskaper för tabellen.
        """
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        table.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

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
            Skapar sidan med backtestinställningar.
        """
        page = QWidget()
        page_layout = self.create_vertical_layout(parent=page)

        settings_group = QGroupBox(self.GROUP_SETTINGS)
        layout = self.create_grid_layout(
            parent=settings_group,
            margin=self.MARGIN,
            horizontal_spacing=self.SETTINGS_SPACING,
            vertical_spacing=self.SETTINGS_SPACING
        )

        layout.addWidget(
            self.competition_label,
            0,
            0
        )

        layout.addWidget(
            self.competition_combo,
            0,
            1
        )

        layout.addWidget(
            self.season_label,
            1,
            0
        )

        layout.addWidget(
            self.season_combo,
            1,
            1
        )

        layout.addWidget(
            self.comparison_label,
            2,
            0
        )

        layout.addWidget(
            self.comparison_combo,
            2,
            1
        )

        button_layout = self.create_horizontal_layout()

        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(
            button_layout,
            3,
            0,
            1,
            2
        )

        progress_layout = self.create_vertical_layout()

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        layout.addLayout(
            progress_layout,
            4,
            0,
            1,
            2
        )

        page_layout.addWidget(settings_group)
        page_layout.addStretch()

        return page

    def _create_results_page(self):
        """
            Skapar resultatsidan.
        """
        page = QWidget()
        page_layout = self.create_vertical_layout(
            parent=page)

        information_layout = self.create_grid_layout()

        information_layout.addWidget(
            self.season_result_label,
            0,
            0
        )

        information_layout.addWidget(
            self.best_result_label,
            1,
            0
        )

        information_layout.setColumnStretch(0, 1)

        page_layout.addLayout(information_layout)
        page_layout.addSpacing(self.SECTION_SPACING)

        results_group = QGroupBox(self.GROUP_RESULTS)
        results_layout = self.create_vertical_layout(parent=results_group)

        results_layout.addWidget(self.result_table)

        page_layout.addWidget(results_group)
        page_layout.addStretch()

        button_layout = self.create_horizontal_layout()

        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.copy_result_button)

        page_layout.addLayout(button_layout)

        return page

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_settings(self):
        """
            Visar inställningssidan.
        """
        self.page_stack.setCurrentWidget(self.settings_page)

    def show_results(self):
        """
            Visar resultatsidan.
        """
        self.page_stack.setCurrentWidget(self.results_page)

    # --------------------------------------------------
    # Tävlingar
    # --------------------------------------------------

    def fill_competition_combo(self, competitions):
        """
            Fyller listan med tävlingar.
        """
        self.competition_combo.blockSignals(True)
        self.competition_combo.clear()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.display_name,
                competition
            )

        self.competition_combo.blockSignals(False)

        if self.competition_combo.count() > 0:
            self.competition_combo.setCurrentIndex(0)
            self.competition_changed.emit()

    def get_selected_competition(self):
        """
            Returnerar vald tävling.
        """
        return self.competition_combo.currentData()

    # --------------------------------------------------
    # Säsonger
    # --------------------------------------------------

    def fill_season_combo(self, seasons):
        """
            Fyller listan med säsonger.
        """
        self.season_combo.blockSignals(True)
        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(
                season.display_name,
                season
            )

        self.season_combo.blockSignals(False)

        if self.season_combo.count() > 0:
            self.season_combo.setCurrentIndex(0)
            self.season_changed.emit()

    def get_selected_season(self):
        """
            Returnerar vald säsong.
        """
        return self.season_combo.currentData()

    # --------------------------------------------------
    # Jämförelsetyp
    # --------------------------------------------------

    def get_selected_comparison_type(self):
        """
            Returnerar vald typ av backtestjämförelse.
        """
        return self.comparison_combo.currentData()

    # --------------------------------------------------
    # Resultat
    # --------------------------------------------------

    def show_result(
        self,
        results,
        comparison_type
    ):
        """
            Visar resultatet för vald typ av backtestjämförelse.
        """
        if not results:
            return

        self.current_results = list(results)
        self.current_comparison_type = comparison_type

        season = self.get_selected_season()

        self.season_result_label.setText(
            season.display_name
            if season is not None
            else self.EMPTY_VALUE
        )

        self._configure_result_table_for_comparison(comparison_type)

        self.fill_result_table(
            results,
            comparison_type
        )

        best_result = min(
            results,
            key=lambda result: (
                result.log_loss,
                result.brier_score
            )
        )

        self.best_result_label.setText(
            self._get_best_result_text(
                best_result,
                comparison_type
            )
        )

        self.copy_result_button.setEnabled(True)
        self.show_results()

    def _configure_result_table_for_comparison(
        self,
        comparison_type
    ):
        """
            Anpassar resultattabellens första kolumn efter jämförelsetypen.
        """
        if comparison_type == self.COMPARISON_TIME_DECAY:
            parameter_header = "Time decay"

        elif comparison_type == self.COMPARISON_HISTORY_YEARS:
            parameter_header = "Historik"

        elif comparison_type == self.COMPARISON_TRAINING_SCOPE:
            parameter_header = "Träningsdata"

        else:
            parameter_header = "Värde"

        headers = list(self.RESULT_HEADERS)
        headers[self.RESULT_COLUMN_PARAMETER] = parameter_header

        self.result_table.setHorizontalHeaderLabels(headers)

    def fill_result_table(
        self,
        results,
        comparison_type
    ):
        """
            Fyller tabellen med resultat för samtliga testade värden.
        """
        self.result_table.clearContents()
        self.result_table.setRowCount(len(results))

        for row, result in enumerate(results):
            values = (
                self._format_parameter_value(
                    result,
                    comparison_type
                ),
                str(result.matches_tested),
                f"{result.brier_score:.4f}",
                f"{result.log_loss:.4f}",
                f"{result.accuracy:.1%}"
            )

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.result_table.setItem(
                    row,
                    column,
                    item
                )

        self._adjust_result_table_height()

    def _format_parameter_value(
        self,
        result,
        comparison_type
    ):
        """
            Formaterar det värde som jämförs i aktuell körning.
        """
        if comparison_type == self.COMPARISON_TIME_DECAY:
            return f"{result.time_decay:.4f}"

        if comparison_type == self.COMPARISON_HISTORY_YEARS:
            return f"{result.history_years} år"

        if comparison_type == self.COMPARISON_TRAINING_SCOPE:
            return self.TRAINING_SCOPE_LABELS.get(
                result.training_scope,
                result.training_scope
            )

        return self.EMPTY_VALUE

    def _get_best_result_text(
        self,
        result,
        comparison_type
    ):
        """
            Returnerar texten för det bästa resultatet.
        """
        value = self._format_parameter_value(
            result,
            comparison_type
        )

        if comparison_type == self.COMPARISON_TIME_DECAY:
            return f"Bästa time decay: {value}"

        if comparison_type == self.COMPARISON_HISTORY_YEARS:
            return f"Bästa historiklängd: {value}"

        if comparison_type == self.COMPARISON_TRAINING_SCOPE:
            return f"Bästa träningsdata: {value}"

        return self.EMPTY_VALUE

    # --------------------------------------------------
    # Kopiering
    # --------------------------------------------------

    def copy_result(self):
        """
            Kopierar det aktuella backtestresultatet till urklipp.
        """
        if (
            not self.current_results
            or self.current_comparison_type is None
        ):
            return

        season = self.get_selected_season()

        title = (
            season.display_name
            if season is not None
            else self.EMPTY_VALUE
        )

        best_result = min(
            self.current_results,
            key=lambda result: (
                result.log_loss,
                result.brier_score
            )
        )

        lines = [
            title,
            self._get_best_result_text(
                best_result,
                self.current_comparison_type
            ),
            "",
            (
                f"{self._get_parameter_header(self.current_comparison_type)}"
                "\tMatcher\tBrier score\tLog loss\tAccuracy"
            )
        ]

        for result in self.current_results:
            lines.append(
                "\t".join(
                    (
                        self._format_parameter_value(
                            result,
                            self.current_comparison_type
                        ),
                        str(result.matches_tested),
                        f"{result.brier_score:.8f}",
                        f"{result.log_loss:.8f}",
                        f"{result.accuracy:.1%}"
                    )
                )
            )

        QGuiApplication.clipboard().setText(
            "\n".join(lines)
        )

    def _get_parameter_header(self, comparison_type):
        """
            Returnerar rubriken för jämförelsens parameterkolumn.
        """
        if comparison_type == self.COMPARISON_TIME_DECAY:
            return "Time decay"

        if comparison_type == self.COMPARISON_HISTORY_YEARS:
            return "Historik"

        if comparison_type == self.COMPARISON_TRAINING_SCOPE:
            return "Träningsdata"

        return "Värde"

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def set_backtest_progress(
        self,
        value,
        text
    ):
        """
            Uppdaterar backtestets
            progress och statustext.
        """
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)

    def reset_backtest_progress(self):
        """
            Återställer progressvisningen.
        """
        self.progress_bar.setValue(0)
        self.progress_label.setText("")

    def set_progress_visible(self, visible):
        """
            Visar eller döljer progressinformationen.
        """
        self.progress_bar.setVisible(visible)
        self.progress_label.setVisible(visible)

    # --------------------------------------------------
    # Tabellstorlek
    # --------------------------------------------------

    def _adjust_result_table_height(self):
        """
            Anpassar resultattabellens höjd efter antalet resultat.
        """
        self.result_table.resizeRowsToContents()

        height = self.result_table.horizontalHeader().height()

        for row in range(self.result_table.rowCount()):
            height += self.result_table.rowHeight(row)

        height += self.result_table.frameWidth() * 2

        self.result_table.setFixedHeight(height)

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_result(self):
        """
            Tömmer tidigare resultat.
        """
        self.current_results = []
        self.current_comparison_type = None

        self.season_result_label.setText(self.EMPTY_VALUE)
        self.best_result_label.setText(self.EMPTY_VALUE)

        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.copy_result_button.setEnabled(False)

    def set_run_button_status(self, status):
        """
            Aktiverar eller inaktiverar backtestknappen.
        """
        self.run_button.setEnabled(status)

    def set_cancel_button_status(self, status):
        """
            Aktiverar eller inaktiverar avbrytknappen.
        """
        self.cancel_button.setEnabled(status)

    def set_backtest_running(self, running):
        """
            Anpassar vyn efter om ett backtest pågår.
        """
        self.run_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)

        self.competition_combo.setEnabled(not running)
        self.season_combo.setEnabled(not running)
        self.comparison_combo.setEnabled(not running)
