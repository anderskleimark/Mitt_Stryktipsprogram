from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QLabel,
    QPushButton
)

from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class BacktestView(View):
    """
        Vy för att genomföra historiska backtester
        av matchanalysmodellen.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()
    run_clicked = Signal()

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Backtesting"

    LABEL_COMPETITION = "Tävling"
    LABEL_SEASON = "Säsong"
    LABEL_START_DATE = "Från datum"
    LABEL_END_DATE = "Till datum"

    LABEL_MATCHES = "Matcher"
    LABEL_BRIER = "Brier score"
    LABEL_LOG_LOSS = "Log loss"
    LABEL_ACCURACY = "Accuracy"

    BUTTON_RUN = "Kör backtest"

    EMPTY_VALUE = "-"

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
        self.create_layout()

        self.setLayout(
            self.layout
        )

        self._setup_signals()
        self.clear_result()

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

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar vykomponenterna.
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

        self.run_button = QPushButton(
            self.BUTTON_RUN
        )

        self.matches_label = QLabel()
        self.brier_label = QLabel()
        self.log_loss_label = QLabel()
        self.accuracy_label = QLabel()

    def create_layout(self):
        """
            Skapar vyens layout.
        """
        selection_layout = self.create_grid_layout()

        selection_layout.addWidget(
            self.competition_label,
            0,
            0
        )

        selection_layout.addWidget(
            self.competition_combo,
            0,
            1
        )

        selection_layout.addWidget(
            self.season_label,
            1,
            0
        )

        selection_layout.addWidget(
            self.season_combo,
            1,
            1
        )

        selection_layout.addWidget(
            self.start_date_label,
            2,
            0
        )

        selection_layout.addWidget(
            self.start_date_edit,
            2,
            1
        )

        selection_layout.addWidget(
            self.end_date_label,
            3,
            0
        )

        selection_layout.addWidget(
            self.end_date_edit,
            3,
            1
        )

        selection_layout.addWidget(
            self.run_button,
            4,
            0,
            1,
            2
        )

        self.layout.addLayout(
            selection_layout
        )

        self.layout.addWidget(
            self.matches_label
        )

        self.layout.addWidget(
            self.brier_label
        )

        self.layout.addWidget(
            self.log_loss_label
        )

        self.layout.addWidget(
            self.accuracy_label
        )

        self.layout.addStretch()

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
        return self.competition_combo.currentData()

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
        return self.season_combo.currentData()

    # --------------------------------------------------
    # Datum
    # --------------------------------------------------

    def set_date_range(
        self,
        start_date,
        end_date
    ):
        """
            Sätter förvalt datumintervall.
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
        result
    ):
        """
            Visar resultatet från ett backtest.
        """
        self.matches_label.setText(
            f"{self.LABEL_MATCHES}: "
            f"{result.matches_tested}"
        )

        self.brier_label.setText(
            f"{self.LABEL_BRIER}: "
            f"{result.brier_score:.4f}"
        )

        self.log_loss_label.setText(
            f"{self.LABEL_LOG_LOSS}: "
            f"{result.log_loss:.4f}"
        )

        self.accuracy_label.setText(
            f"{self.LABEL_ACCURACY}: "
            f"{result.accuracy:.1%}"
        )

    def clear_result(self):
        """
            Tömmer tidigare backtestresultat.
        """
        self.matches_label.setText(
            f"{self.LABEL_MATCHES}: "
            f"{self.EMPTY_VALUE}"
        )

        self.brier_label.setText(
            f"{self.LABEL_BRIER}: "
            f"{self.EMPTY_VALUE}"
        )

        self.log_loss_label.setText(
            f"{self.LABEL_LOG_LOSS}: "
            f"{self.EMPTY_VALUE}"
        )

        self.accuracy_label.setText(
            f"{self.LABEL_ACCURACY}: "
            f"{self.EMPTY_VALUE}"
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

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
