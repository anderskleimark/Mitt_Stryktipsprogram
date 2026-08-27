from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
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

        Vyn består av en inställningssida och en
        separat resultatsida där flera time-decay-
        värden jämförs.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()

    run_clicked = Signal()
    back_clicked = Signal()

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Backtesting"

    GROUP_SETTINGS = "Inställningar"
    GROUP_RESULTS = "Jämförelse av time decay"

    LABEL_COMPETITION = "Tävling"
    LABEL_SEASON = "Säsong"

    LABEL_START_DATE = "Från datum"
    LABEL_END_DATE = "Till datum"

    BUTTON_RUN = "Kör backtest"
    BUTTON_BACK = "Tillbaka"

    EMPTY_VALUE = "-"

    # --------------------------------------------------
    # Resultattabell
    # --------------------------------------------------

    RESULT_HEADERS = (
        "Time decay",
        "Matcher",
        "Brier score",
        "Log loss",
        "Accuracy"
    )

    RESULT_COLUMN_TIME_DECAY = 0
    RESULT_COLUMN_MATCHES = 1
    RESULT_COLUMN_BRIER = 2
    RESULT_COLUMN_LOG_LOSS = 3
    RESULT_COLUMN_ACCURACY = 4

    RESULT_COLUMN_COUNT = 5

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    SECTION_SPACING = 12
    SETTINGS_SPACING = 10

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self):
        """
            Initierar backtestvyn.
        """
        super().__init__()

        self.layout = self.create_main_layout()

        self.create_header(
            self.VIEW_TITLE
        )

        self.layout.addWidget(
            self.header
        )

        self.create_widgets()
        self.create_pages()

        self.layout.addWidget(
            self.page_stack,
            stretch=1
        )

        self.setLayout(
            self.layout
        )

        self._setup_signals()

        self.clear_result()
        self.set_run_button_status(False)

        self.show_settings()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar widgetarnas signaler till
            vyklassens egna signaler.
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

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar samtliga widgetar.
        """
        self._create_selection_widgets()
        self._create_result_widgets()

        self.run_button = QPushButton(
            self.BUTTON_RUN
        )

        self.back_button = QPushButton(
            self.BUTTON_BACK
        )

    def _create_selection_widgets(self):
        """
            Skapar widgetar för
            backtestinställningarna.
        """
        self.competition_label = QLabel(
            self.LABEL_COMPETITION
        )

        self.competition_combo = BaseComboBox()

        self.season_label = QLabel(
            self.LABEL_SEASON
        )

        self.season_combo = BaseComboBox()

        self.start_date_label = QLabel(
            self.LABEL_START_DATE
        )

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(
            True
        )
        self.start_date_edit.setDisplayFormat(
            "yyyy-MM-dd"
        )

        self.end_date_label = QLabel(
            self.LABEL_END_DATE
        )

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(
            True
        )
        self.end_date_edit.setDisplayFormat(
            "yyyy-MM-dd"
        )

    def _create_result_widgets(self):
        """
            Skapar resultatöversikten.
        """
        self.season_result_label = QLabel()
        self.period_result_label = QLabel()

        self.season_result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.period_result_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.result_table = QTableWidget()

        self.result_table.setColumnCount(
            self.RESULT_COLUMN_COUNT
        )

        self.result_table.setHorizontalHeaderLabels(
            self.RESULT_HEADERS
        )

        self._configure_table(
            self.result_table
        )

        self.result_table.verticalHeader().setVisible(
            False
        )

        header = (
            self.result_table
            .horizontalHeader()
        )

        for column in range(
            self.RESULT_COLUMN_COUNT
        ):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

    def _configure_table(
        self,
        table
    ):
        """
            Ställer in gemensamma egenskaper
            för tabellen.
        """
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )

        table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

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

        self.settings_page = (
            self._create_settings_page()
        )

        self.results_page = (
            self._create_results_page()
        )

        self.page_stack.addWidget(
            self.settings_page
        )

        self.page_stack.addWidget(
            self.results_page
        )

    def _create_settings_page(self):
        """
            Skapar sidan med
            backtestinställningar.
        """
        page = QWidget()

        page_layout = QVBoxLayout(
            page
        )

        settings_group = QGroupBox(
            self.GROUP_SETTINGS
        )

        layout = QGridLayout(
            settings_group
        )

        layout.setHorizontalSpacing(
            self.SETTINGS_SPACING
        )

        layout.setVerticalSpacing(
            self.SETTINGS_SPACING
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
            self.start_date_label,
            2,
            0
        )

        layout.addWidget(
            self.start_date_edit,
            2,
            1
        )

        layout.addWidget(
            self.end_date_label,
            3,
            0
        )

        layout.addWidget(
            self.end_date_edit,
            3,
            1
        )

        layout.addWidget(
            self.run_button,
            4,
            0,
            1,
            2
        )

        page_layout.addWidget(
            settings_group
        )

        page_layout.addStretch()

        return page

    def _create_results_page(self):
        """
            Skapar resultatsidan.
        """
        page = QWidget()

        page_layout = QVBoxLayout(
            page
        )

        # --------------------------------------------------
        # Information om körningen
        # --------------------------------------------------

        information_layout = QGridLayout()

        information_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        information_layout.addWidget(
            self.season_result_label,
            0,
            0
        )

        information_layout.addWidget(
            self.period_result_label,
            0,
            1
        )

        information_layout.setColumnStretch(
            0,
            1
        )

        information_layout.setColumnStretch(
            1,
            1
        )

        page_layout.addLayout(
            information_layout
        )

        page_layout.addSpacing(
            self.SECTION_SPACING
        )

        # --------------------------------------------------
        # Resultat
        # --------------------------------------------------

        results_group = QGroupBox(
            self.GROUP_RESULTS
        )

        results_layout = QVBoxLayout(
            results_group
        )

        results_layout.addWidget(
            self.result_table
        )

        page_layout.addWidget(
            results_group
        )

        page_layout.addStretch()

        page_layout.addWidget(
            self.back_button
        )

        return page

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_settings(self):
        """
            Visar inställningssidan.
        """
        self.page_stack.setCurrentWidget(
            self.settings_page
        )

    def show_results(self):
        """
            Visar resultatsidan.
        """
        self.page_stack.setCurrentWidget(
            self.results_page
        )

    # --------------------------------------------------
    # Tävlingar
    # --------------------------------------------------

    def fill_competition_combo(
        self,
        competitions
    ):
        """
            Fyller listan med tävlingar.
        """
        self.competition_combo.clear()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.display_name,
                competition
            )

    def get_selected_competition(self):
        """
            Returnerar vald tävling.
        """
        return (
            self.competition_combo
            .currentData()
        )

    # --------------------------------------------------
    # Säsonger
    # --------------------------------------------------

    def fill_season_combo(
        self,
        seasons
    ):
        """
            Fyller listan med säsonger.
        """
        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(
                season.display_name,
                season
            )

    def get_selected_season(self):
        """
            Returnerar vald säsong.
        """
        return (
            self.season_combo
            .currentData()
        )

    # --------------------------------------------------
    # Datum
    # --------------------------------------------------

    def set_date_range(
        self,
        start_date,
        end_date
    ):
        """
            Sätter datumintervallet.
        """
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
        """
            Returnerar valt startdatum.
        """
        return (
            self.start_date_edit
            .date()
            .toPython()
        )

    def get_end_date(self):
        """
            Returnerar valt slutdatum.
        """
        return (
            self.end_date_edit
            .date()
            .toPython()
        )

    # --------------------------------------------------
    # Resultat
    # --------------------------------------------------

    def show_result(
        self,
        results
    ):
        """
            Visar jämförelsen mellan de
            testade time-decay-värdena.
        """
        season = (
            self.get_selected_season()
        )

        start_date = (
            self.get_start_date()
        )

        end_date = (
            self.get_end_date()
        )

        self.season_result_label.setText(
            season.display_name
            if season is not None
            else self.EMPTY_VALUE
        )

        self.period_result_label.setText(
            f"Period: "
            f"{start_date:%Y-%m-%d} – "
            f"{end_date:%Y-%m-%d}"
        )

        self.fill_result_table(
            results
        )

        self.show_results()

    def fill_result_table(
        self,
        results
    ):
        """
            Fyller tabellen med resultat
            för samtliga time-decay-värden.
        """
        self.result_table.setRowCount(
            len(results)
        )

        for row, result in enumerate(
            results
        ):
            values = (
                f"{result.time_decay:.3f}",
                str(result.matches_tested),
                f"{result.brier_score:.4f}",
                f"{result.log_loss:.4f}",
                f"{result.accuracy:.1%}"
            )

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    value
                )

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.result_table.setItem(
                    row,
                    column,
                    item
                )

        self._adjust_result_table_height()

    # --------------------------------------------------
    # Tabellstorlek
    # --------------------------------------------------

    def _adjust_result_table_height(self):
        """
            Anpassar resultattabellens höjd
            efter antalet time-decay-värden.
        """
        self.result_table.resizeRowsToContents()

        height = (
            self.result_table
            .horizontalHeader()
            .height()
        )

        for row in range(
            self.result_table.rowCount()
        ):
            height += (
                self.result_table
                .rowHeight(row)
            )

        height += (
            self.result_table.frameWidth()
            * 2
        )

        self.result_table.setFixedHeight(
            height
        )

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_result(self):
        """
            Tömmer tidigare resultat.
        """
        self.season_result_label.setText(
            self.EMPTY_VALUE
        )

        self.period_result_label.setText(
            self.EMPTY_VALUE
        )

        self.result_table.setRowCount(
            0
        )

    def set_run_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            backtestknappen.
        """
        self.run_button.setEnabled(
            status
        )
