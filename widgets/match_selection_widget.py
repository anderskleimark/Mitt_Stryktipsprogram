from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel

from misc.buttons import AnalyzeButton, ClearButton
from misc.combo_boxes.base_combo_box import BaseComboBox
from widgets.base_widget import BaseWidget


class MatchSelectionWidget(BaseWidget):
    """
        Widget för val av tävling, säsong
        och lag inför en matchanalys.

        Widgeten innehåller comboboxar för liga,
        säsong, hemmalag och bortalag samt knappar
        för att genomföra eller rensa analysen.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()
    home_team_changed = Signal()
    away_team_changed = Signal()

    analyze_clicked = Signal()
    clear_clicked = Signal()

    # --------------------------------------------------
    # Konstanter
    # --------------------------------------------------

    NO_ROW_SELECTED = -1
    BUTTON_FIXED_WIDTH = 110

    TOP_MARGIN = 20
    BOTTOM_MARGIN = 20
    HORIZONTAL_SPACING = 10
    VERTICAL_SPACING = 10

    LABEL_LEAGUE = "Liga"
    LABEL_SEASON = "Säsong"
    LABEL_HOME_TEAM = "Hemmalag"
    LABEL_AWAY_TEAM = "Bortalag"

    def __init__(self):
        """
            Initierar widgeten och skapar
            dess kontroller och signalanslutningar.
        """
        super().__init__()

        # Comboboxar
        self.competition_combo = None
        self.season_combo = None
        self.home_team_combo = None
        self.away_team_combo = None

        # Knappar
        self.clear_button = None
        self.analyze_button = None

        self._build_widget()
        self._setup_signals()

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def _build_widget(self):
        """
            Skapar widgetens layout och kontroller
            för val av tävling, säsong och lag.
        """
        layout = self.create_grid_layout(
            parent=self,
            horizontal_spacing=self.HORIZONTAL_SPACING,
            vertical_spacing=self.VERTICAL_SPACING
        )

        # Comboboxar
        self.competition_combo = BaseComboBox()
        self.season_combo = BaseComboBox()
        self.home_team_combo = BaseComboBox()
        self.away_team_combo = BaseComboBox()

        # Knappar
        self.clear_button = ClearButton()
        self.analyze_button = AnalyzeButton()

        self.clear_button.setFixedWidth(self.BUTTON_FIXED_WIDTH)
        self.analyze_button.setFixedWidth(self.BUTTON_FIXED_WIDTH)

        self.analyze_button.setDefault(True)
        self.analyze_button.setAutoDefault(True)

        # Liga
        layout.addWidget(
            QLabel(self.LABEL_LEAGUE),
            0,
            0
        )

        layout.addWidget(
            self.competition_combo,
            0,
            1
        )

        # Säsong
        layout.addWidget(
            QLabel(self.LABEL_SEASON),
            0,
            2
        )

        layout.addWidget(
            self.season_combo,
            0,
            3
        )

        # Rensa
        layout.addWidget(
            self.clear_button,
            0,
            4
        )

        # Hemmalag
        layout.addWidget(
            QLabel(self.LABEL_HOME_TEAM),
            1,
            0
        )

        layout.addWidget(
            self.home_team_combo,
            1,
            1
        )

        # Bortalag
        layout.addWidget(
            QLabel(self.LABEL_AWAY_TEAM),
            1,
            2
        )

        layout.addWidget(
            self.away_team_combo,
            1,
            3
        )

        # Analysera
        layout.addWidget(
            self.analyze_button,
            1,
            4
        )

        layout.setColumnStretch(
            1,
            3
        )

        layout.setColumnStretch(
            3,
            3
        )

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Vidarebefordrar ändringar i comboboxarna
            och knapptryckningar genom widgetens
            egna signaler.
        """
        self.competition_combo.currentIndexChanged.connect(
            lambda _: self.competition_changed.emit()
        )

        self.season_combo.currentIndexChanged.connect(
            lambda _: self.season_changed.emit()
        )

        self.home_team_combo.currentIndexChanged.connect(
            lambda _: self.home_team_changed.emit()
        )

        self.away_team_combo.currentIndexChanged.connect(
            lambda _: self.away_team_changed.emit()
        )

        self.analyze_button.clicked.connect(
            self.analyze_clicked.emit
        )

        self.clear_button.clicked.connect(
            self.clear_clicked.emit
        )

    # --------------------------------------------------
    # Fyll comboboxar
    # --------------------------------------------------

    def fill_competition_combo(
        self,
        competitions=None
    ):
        """
            Fyller comboboxen med tillgängliga
            tävlingar och återställer aktuellt val.
        """
        if competitions is None:
            competitions = []

        self.competition_combo.blockSignals(True)
        self.competition_combo.clear()

        for competition in competitions:
            self.competition_combo.addItem(competition.display_name)

        self.competition_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.competition_combo.blockSignals(False)

    def fill_season_combo(
        self,
        seasons=None
    ):
        """
            Fyller comboboxen med tillgängliga säsonger och återställer aktuellt val.
        """
        if seasons is None:
            seasons = []

        self.season_combo.blockSignals(True)
        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(season.display_name)

        self.season_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.season_combo.blockSignals(False)

    def fill_team_combos(
        self,
        teams
    ):
        """
            Fyller comboboxarna för hemma- och bortalag med angivna lag.
        """
        self.fill_home_team_combo(teams)
        self.fill_away_team_combo(teams)

    def fill_home_team_combo(
        self,
        teams=None
    ):
        """
            Fyller comboboxen med tillgängliga hemmalag och återställer aktuellt val.
        """
        if teams is None:
            teams = []

        self.home_team_combo.blockSignals(True)
        self.home_team_combo.clear()

        for team in teams:
            self.home_team_combo.addItem(
                team.display_name,
                team
            )

        self.home_team_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.home_team_combo.blockSignals(False)

    def fill_away_team_combo(
        self,
        teams=None
    ):
        """
            Fyller comboboxen med tillgängliga bortalag och återställer aktuellt val.
        """
        if teams is None:
            teams = []

        self.away_team_combo.blockSignals(True)
        self.away_team_combo.clear()

        for team in teams:
            self.away_team_combo.addItem(
                team.display_name,
                team
            )

        self.away_team_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.away_team_combo.blockSignals(False)

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def set_competition_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar comboboxen för tävling.
        """
        self.competition_combo.setEnabled(status)

    def set_season_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            comboboxen för säsong.
        """
        self.season_combo.setEnabled(status)

    def set_home_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar comboboxen för hemmalag.
        """
        self.home_team_combo.setEnabled(status)

    def set_away_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar comboboxen för bortalag.
        """
        self.away_team_combo.setEnabled(status)

    def set_analyze_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            analysknappen.
        """
        self.analyze_button.setEnabled(status)

    def set_clear_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            rensningsknappen.
        """
        self.clear_button.setEnabled(status)

    # --------------------------------------------------
    # Återställning
    # --------------------------------------------------

    def reset(self):
        """
            Återställer samtliga comboboxar
            till läget utan aktuellt val.

            Signaler blockeras under återställningen
            för att undvika oönskade signaler till
            controllern.
        """
        combos = (
            self.competition_combo,
            self.season_combo,
            self.home_team_combo,
            self.away_team_combo
        )

        for combo in combos:
            combo.blockSignals(True)

        for combo in combos:
            combo.setCurrentIndex(self.NO_ROW_SELECTED)

        for combo in combos:
            combo.blockSignals(False)

    # --------------------------------------------------
    # Valda objekt
    # --------------------------------------------------

    def get_selected_home_team(self):
        """
            Returnerar det valda hemmalagets Team-objekt.

            Returnerar None om inget hemmalag är valt.
        """
        return self.home_team_combo.currentData()

    def get_selected_away_team(self):
        """
            Returnerar det valda bortalagets Team-objekt.

            Returnerar None om inget bortalag är valt.
        """
        return self.away_team_combo.currentData()

    def get_selected_competition_row(self):
        """
            Returnerar index för vald tävling.

            Returnerar -1 om ingen tävling
            är vald.
        """
        return self.competition_combo.currentIndex()

    def get_selected_season_row(self):
        """
            Returnerar index för vald säsong.

            Returnerar -1 om ingen säsong är vald.
        """
        return self.season_combo.currentIndex()
