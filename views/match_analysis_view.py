from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHeaderView, QLabel,
                               QStackedWidget, QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (AnalyzeButton, ClearButton, OddsButton,
                          PoissonButton, ProbabilityButton, StatisticButton)
from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class MatchAnalysisView(View):
    """
        Klass som visar och presenterar analys av en fotbollsmatch.
    """

    # --------------------------------------------------
    # Tabeller
    # --------------------------------------------------

    TABLE_ROWS = 2

    STATISTICS_COLUMNS = 7
    MODEL_COLUMNS = 7
    H2H_COLUMNS = 6

    POISSON_ROWS = 6
    POISSON_COLUMNS = 2

    # --------------------------------------------------
    # Statistik-kolumner
    # --------------------------------------------------

    COLUMN_TEAM = 0
    COLUMN_MATCHES = 1
    COLUMN_WINS = 2
    COLUMN_DRAWS = 3
    COLUMN_LOSSES = 4
    COLUMN_GOALS = 5
    COLUMN_GOAL_DIFFERENCE = 6

    # --------------------------------------------------
    # Modell-kolumner
    # --------------------------------------------------

    MODEL_COLUMN_TEAM = 0
    MODEL_COLUMN_LAMBDA = 1
    MODEL_COLUMN_ATTACK = 2
    MODEL_COLUMN_DEFENCE = 3
    MODEL_COLUMN_AVG_GOALS_FOR = 4
    MODEL_COLUMN_AVG_GOALS_AGAINST = 5
    MODEL_COLUMN_FORM = 6

    # --------------------------------------------------
    # H2H-kolumner
    # --------------------------------------------------

    H2H_COLUMN_TEAM = 0
    H2H_COLUMN_PLAYED = 1
    H2H_COLUMN_WINS = 2
    H2H_COLUMN_DRAWS = 3
    H2H_COLUMN_LOSSES = 4
    H2H_COLUMN_GOALS = 5

    # --------------------------------------------------
    # Rubriker
    # --------------------------------------------------

    STATISTICS_HEADERS = (
        "Lag",
        "Sp",
        "V",
        "O",
        "F",
        "Mål",
        "Δ"
    )

    MODEL_HEADERS = (
        "Lag",
        "λ",
        "Attack",
        "Försvar",
        "GF/M",
        "GA/M",
        "Form"
    )

    H2H_HEADERS = (
        "Lag",
        "Sp",
        "V",
        "O",
        "F",
        "Resultat"
    )

    POISSON_HEADERS = (
        "Mål",
        "Sannolikhet"
    )

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Matchanalys"

    LABEL_LEAGUE = "Liga"
    LABEL_SEASON = "Säsong"
    LABEL_HOME_TEAM = "Hemmalag"
    LABEL_AWAY_TEAM = "Bortalag"

    LABEL_TOTAL = "Totalt"
    LABEL_VENUE = "Hemma/Borta"
    LABEL_MODEL = "Modellparametrar"
    LABEL_H2H = "Inbördes möten"

    LABEL_PROBABILITY = "Sannolikheter"
    LABEL_ODDS = "Oddsanalys"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    BUTTON_FIXED_WIDTH = 110

    MATCH_SELECTION_TOP_MARGIN = 20
    MATCH_SELECTION_BOTTOM_MARGIN = 20
    MATCH_SELECTION_HORIZONTAL_SPACING = 10
    MATCH_SELECTION_VERTICAL_SPACING = 10

    ANALYSIS_PAGE_SPACING = 1
    NAVIGATION_SPACING = None

    FLAG_TABLE_SPACING = 1

    def __init__(self):
        super().__init__()

        # Sidor
        self.statistics_page = None
        self.poisson_page = None
        self.probability_page = None
        self.odds_page = None

        # Tabeller
        self.total_table = None
        self.venue_table = None
        self.model_table = None
        self.home_poisson_table = None
        self.away_poisson_table = None
        self.h2h_table = None

        # Widgetar och knappar
        self.navigation_widget = None

        self.statistics_button = None
        self.poisson_button = None
        self.probability_button = None
        self.odds_button = None

        # Etiketter
        self.home_lambda_label = None
        self.away_lambda_label = None

        # Huvudlayout
        self.layout = self.create_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self._create_match_selection_widget()
        self._create_analysis_widget()

        self.setLayout(self.layout)

    # --------------------------------------------------
    # Matchval
    # --------------------------------------------------

    def _create_match_selection_widget(self):
        """
            Skapar widgeten för val av liga, säsong och lag.
        """
        self.match_selection_widget = QWidget()

        layout = QGridLayout(
            self.match_selection_widget
        )

        layout.setContentsMargins(
            0,
            self.MATCH_SELECTION_TOP_MARGIN,
            0,
            self.MATCH_SELECTION_BOTTOM_MARGIN
        )

        layout.setHorizontalSpacing(
            self.MATCH_SELECTION_HORIZONTAL_SPACING
        )

        layout.setVerticalSpacing(
            self.MATCH_SELECTION_VERTICAL_SPACING
        )

        # Combo-boxar
        self.competition_combo = BaseComboBox()
        self.season_combo = BaseComboBox()
        self.home_team_combo = BaseComboBox()
        self.away_team_combo = BaseComboBox()

        # Knappar
        self.clear_button = ClearButton()
        self.analyze_button = AnalyzeButton()

        self.clear_button.setFixedWidth(
            self.BUTTON_FIXED_WIDTH
        )

        self.analyze_button.setFixedWidth(
            self.BUTTON_FIXED_WIDTH
        )
        self.analyze_button.setDefault(True)
        self.analyze_button.setAutoDefault(True)

        # Rad 1
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

        layout.addWidget(
            self.clear_button,
            0,
            4
        )

        # Rad 2
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

        layout.addWidget(
            self.analyze_button,
            1,
            4
        )

        # Ge comboboxarna plats
        layout.setColumnStretch(
            1,
            3
        )

        layout.setColumnStretch(
            3,
            3
        )

        self.layout.addWidget(
            self.match_selection_widget
        )

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setFrameShadow(
            QFrame.Shadow.Sunken
        )

        self.layout.addWidget(
            separator
        )

    # --------------------------------------------------
    # Analysyta
    # --------------------------------------------------

    def _create_analysis_widget(self):
        """
            Skapar analysytan med stackade sidor
            och navigering längst ned.
        """
        self.analysis_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.analysis_widget,
            spacing=self.ANALYSIS_PAGE_SPACING
        )

        self.analysis_stack = QStackedWidget()

        self._create_statistics_page()
        self._create_poisson_page()
        self._create_probability_page()
        self._create_odds_page()

        layout.addWidget(
            self.analysis_stack,
            stretch=1
        )

        self._create_navigation()

        layout.addWidget(
            self.navigation_widget
        )

        self.layout.addWidget(
            self.analysis_widget
        )

    # --------------------------------------------------
    # Statistik
    # --------------------------------------------------

    def _create_statistics_page(self):
        """
            Skapar sidan med statistiktabeller.
        """
        self.statistics_page = QWidget()

        layout = QGridLayout(
            self.statistics_page
        )

        self.total_table = self._create_table(
            self.STATISTICS_COLUMNS,
            self.STATISTICS_HEADERS,
            self.COLUMN_TEAM
        )

        self.venue_table = self._create_table(
            self.STATISTICS_COLUMNS,
            self.STATISTICS_HEADERS,
            self.COLUMN_TEAM
        )

        self.model_table = self._create_table(
            self.MODEL_COLUMNS,
            self.MODEL_HEADERS,
            self.MODEL_COLUMN_TEAM
        )

        self.h2h_table = self._create_table(
            self.H2H_COLUMNS,
            self.H2H_HEADERS,
            self.H2H_COLUMN_TEAM
        )

        # Övre raden
        layout.addWidget(
            QLabel(self.LABEL_TOTAL),
            1,
            0
        )

        layout.addWidget(
            QLabel(self.LABEL_VENUE),
            1,
            1
        )

        layout.addWidget(
            self.total_table,
            2,
            0
        )

        layout.addWidget(
            self.venue_table,
            2,
            1
        )

        # Nedre raden
        layout.addWidget(
            QLabel(self.LABEL_MODEL),
            3,
            0
        )

        layout.addWidget(
            QLabel(self.LABEL_H2H),
            3,
            1
        )

        layout.addWidget(
            self.model_table,
            4,
            0
        )

        layout.addWidget(
            self.h2h_table,
            4,
            1
        )

        layout.setColumnStretch(
            0,
            1
        )

        layout.setColumnStretch(
            1,
            1
        )

        self.analysis_stack.addWidget(
            self.statistics_page
        )

    # --------------------------------------------------
    # Poisson
    # --------------------------------------------------

    def _create_poisson_page(self):
        """
            Skapar sidan för Poisson-analys.
        """
        self.poisson_page = QWidget()

        layout = self.create_horizontal_sub_layout(
            parent=self.poisson_page,
            spacing=None
        )

        # Hemmalag
        home_widget = QWidget()

        home_layout = self.create_vertical_sub_layout(
            parent=home_widget,
            spacing=1
        )

        home_label = QLabel(
            self.LABEL_HOME_TEAM
        )

        self.home_lambda_label = QLabel(
            "λ = -"
        )

        self.home_lambda_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.home_poisson_table = (
            self._create_poisson_table()
        )

        home_layout.addWidget(
            home_label
        )

        home_layout.addWidget(
            self.home_lambda_label
        )

        home_layout.addWidget(
            self.home_poisson_table
        )

        # Bortalag
        away_widget = QWidget()

        away_layout = self.create_vertical_sub_layout(
            parent=away_widget,
            spacing=1
        )

        away_label = QLabel(
            self.LABEL_AWAY_TEAM
        )

        self.away_lambda_label = QLabel(
            "λ = -"
        )

        self.away_lambda_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.away_poisson_table = (
            self._create_poisson_table()
        )

        away_layout.addWidget(
            away_label
        )

        away_layout.addWidget(
            self.away_lambda_label
        )

        away_layout.addWidget(
            self.away_poisson_table
        )

        layout.addWidget(
            home_widget
        )

        layout.addWidget(
            away_widget
        )

        self.analysis_stack.addWidget(
            self.poisson_page
        )

    # --------------------------------------------------
    # Sannolikheter
    # --------------------------------------------------

    def _create_probability_page(self):
        """
            Skapar sidan med sannolikheter.
        """
        self.probability_page = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.probability_page,
            spacing=None
        )

        label = QLabel(
            self.LABEL_PROBABILITY
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            label
        )

        self.analysis_stack.addWidget(
            self.probability_page
        )

    # --------------------------------------------------
    # Odds
    # --------------------------------------------------

    def _create_odds_page(self):
        """
            Skapar sidan med oddsanalys.
        """
        self.odds_page = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.odds_page,
            spacing=None
        )

        label = QLabel(
            self.LABEL_ODDS
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            label
        )

        self.analysis_stack.addWidget(
            self.odds_page
        )

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def _create_navigation(self):
        """
            Skapar navigeringsknapparna.
        """
        self.navigation_widget = QWidget()

        layout = self.create_horizontal_sub_layout(
            parent=self.navigation_widget,
            spacing=self.NAVIGATION_SPACING
        )

        self.statistics_button = StatisticButton()

        self.poisson_button = PoissonButton()

        self.probability_button = ProbabilityButton()

        self.odds_button = OddsButton()

        layout.addWidget(
            self.statistics_button
        )

        layout.addWidget(
            self.poisson_button
        )

        layout.addWidget(
            self.probability_button
        )

        layout.addWidget(
            self.odds_button
        )

    # --------------------------------------------------
    # Combo-boxar
    # --------------------------------------------------

    def fill_competition_combo(
        self,
        competitions=None
    ):
        """
        Fyller listan med tillgängliga ligor.
        """
        if competitions is None:
            competitions = []

        self.competition_combo.blockSignals(
            True
        )

        self.competition_combo.clear_with_empty_item()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.name
            )

        self.competition_combo.blockSignals(
            False
        )

    def fill_season_combo(
        self,
        seasons=None
    ):
        """
            Fyller listan med tillgängliga säsonger.
        """
        if seasons is None:
            seasons = []

        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(
                season.name
            )

    def fill_team_combos(self, teams):
        """
            Fyller hemma- och bortalagslistorna.
        """
        self.home_team_combo.blockSignals(
            True
        )

        self.away_team_combo.blockSignals(
            True
        )

        self.fill_home_team_combo(
            teams
        )

        self.fill_away_team_combo(
            teams
        )

        self.home_team_combo.blockSignals(
            False
        )

        self.away_team_combo.blockSignals(
            False
        )

    def fill_home_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med hemmalag.
        """
        if teams is None:
            teams = []

        self.home_team_combo.clear_with_empty_item()

        for team in teams:
            self.home_team_combo.addItem(
                team.name,
                team
            )

    def fill_away_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med bortalag.
        """
        if teams is None:
            teams = []

        self.away_team_combo.clear_with_empty_item()

        for team in teams:
            self.away_team_combo.addItem(
                team.name,
                team
            )

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(self, analysis):
        """
            Visar resultatet av en matchanalys.
        """
        home = analysis.home_statistics
        away = analysis.away_statistics

        self._fill_table(
            self.total_table,
            [
                self._get_total_statistics_row(home),
                self._get_total_statistics_row(away)
            ]
        )

        self._fill_table(
            self.venue_table,
            [
                self._get_home_statistics_row(home),
                self._get_away_statistics_row(away)
            ]
        )

        self._fill_table(
            self.model_table,
            [
                self._get_home_model_row(analysis),
                self._get_away_model_row(analysis)
            ]
        )

        self._fill_table(
            self.h2h_table,
            self._get_h2h_rows(analysis)
        )

        self._fill_poisson_table(
            self.home_poisson_table,
            analysis.home_poisson
        )

        self._fill_poisson_table(
            self.away_poisson_table,
            analysis.away_poisson
        )

        self.home_lambda_label.setText(
            f"λ = {analysis.lambda_home:.2f}"
        )

        self.away_lambda_label.setText(
            f"λ = {analysis.lambda_away:.2f}"
        )

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_statistics(self):
        self.analysis_stack.setCurrentWidget(
            self.statistics_page
        )

    def show_poisson(self):
        self.analysis_stack.setCurrentWidget(
            self.poisson_page
        )

    def show_probabilities(self):
        self.analysis_stack.setCurrentWidget(
            self.probability_page
        )

    def show_odds(self):
        self.analysis_stack.setCurrentWidget(
            self.odds_page
        )

    # --------------------------------------------------
    # Tabellskapande
    # --------------------------------------------------

    def _create_table(
        self,
        columns,
        headers,
        wide_column
    ):
        """
            Skapar en tabell med angivna kolumner
            och rubriker.
        """
        table = BaseTableWidget(
            readonly=True,
            rowselection=False,
            rows=self.TABLE_ROWS,
            cols=columns
        )

        table.setHorizontalHeaderLabels(
            headers
        )

        table.verticalHeader().setVisible(
            False
        )

        table.set_wide_column(
            wide_column
        )

        table.set_narrow_columns(
            range(
                wide_column + 1,
                columns
            )
        )

        table.set_no_selection()

        return table

    def _create_poisson_table(self):
        """
            Skapar en tabell för Poisson-fördelningen.
        """
        table = BaseTableWidget(
            readonly=True,
            rowselection=False,
            rows=self.POISSON_ROWS,
            cols=self.POISSON_COLUMNS
        )

        table.setHorizontalHeaderLabels(
            self.POISSON_HEADERS
        )

        table.verticalHeader().setVisible(
            False
        )

        header = table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table.set_no_selection()

        return table

    # --------------------------------------------------
    # Tabelluppdatering
    # --------------------------------------------------

    def _center_table_columns(self, table):
        """
            Centrerar tabellens numeriska kolumner.
        """
        for column in range(
            self.COLUMN_MATCHES,
            table.columnCount()
        ):
            table.center_column(
                column
            )

    def _fill_table(
        self,
        table,
        table_rows
    ):
        """
            Fyller en tabell med data.
        """
        table.clearContents()

        for row, values in enumerate(
            table_rows
        ):
            for column, value in enumerate(
                values
            ):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self._center_table_columns(
            table
        )

    def _fill_poisson_table(
        self,
        table,
        distribution
    ):
        """
            Fyller en Poisson-tabell.
        """
        table.clearContents()

        last_index = (
            len(distribution) - 1
        )

        for goals, probability in enumerate(
            distribution
        ):
            goal_text = (
                f"{goals}+"
                if goals == last_index
                else str(goals)
            )

            table.setItem(
                goals,
                0,
                QTableWidgetItem(
                    goal_text
                )
            )

            table.setItem(
                goals,
                1,
                QTableWidgetItem(
                    f"{probability:.1%}".replace(
                        "%",
                        " %"
                    )
                )
            )

            table.center_column(0)
            table.center_column(1)

    # --------------------------------------------------
    # Statistikrader
    # --------------------------------------------------

    def _get_total_statistics_row(
        self,
        statistics
    ):
        return [
            statistics.team.name,
            statistics.matches_played,
            statistics.wins,
            statistics.draws,
            statistics.losses,
            statistics.goals_for_against,
            statistics.goal_difference
        ]

    def _get_home_statistics_row(
        self,
        statistics
    ):
        return [
            statistics.team.name,
            statistics.home_matches_played,
            statistics.home_wins,
            statistics.home_draws,
            statistics.home_losses,
            statistics.home_goals_for_against,
            statistics.home_goal_difference
        ]

    def _get_away_statistics_row(
        self,
        statistics
    ):
        return [
            statistics.team.name,
            statistics.away_matches_played,
            statistics.away_wins,
            statistics.away_draws,
            statistics.away_losses,
            statistics.away_goals_for_against,
            statistics.away_goal_difference
        ]

    def _get_home_model_row(
        self,
        analysis
    ):
        statistics = (
            analysis.home_statistics
        )

        return [
            statistics.team.name,
            f"{analysis.lambda_home:.2f}",
            f"{statistics.home_attack_coefficient:.2f}",
            f"{1 / statistics.home_defence_coefficient:.2f}",
            f"{statistics.average_home_goals_for:.2f}",
            f"{statistics.average_home_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        ]

    def _get_away_model_row(
        self,
        analysis
    ):
        statistics = (
            analysis.away_statistics
        )

        return [
            statistics.team.name,
            f"{analysis.lambda_away:.2f}",
            f"{statistics.away_attack_coefficient:.2f}",
            f"{1 / statistics.away_defence_coefficient:.2f}",
            f"{statistics.average_away_goals_for:.2f}",
            f"{statistics.average_away_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        ]

    def _get_h2h_rows(
        self,
        analysis
    ):
        h2h = analysis.h2h_statistics

        return [
            [
                analysis.home_statistics.team.name,
                h2h.matches,
                h2h.home_wins,
                h2h.home_draws,
                h2h.home_losses,
                h2h.home_score
            ],
            [
                analysis.away_statistics.team.name,
                h2h.matches,
                h2h.away_wins,
                h2h.away_draws,
                h2h.away_losses,
                h2h.away_score
            ]
        ]

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def enter_pre_analyze_state(self):
        """
            Återställer vyn inför en ny matchanalys.
        """
        self.clear_analysis()
        self.enable_navigation(False)

        self.competition_combo.setEnabled(True)
        self.season_combo.setEnabled(True)
        self.home_team_combo.setEnabled(True)
        self.away_team_combo.setEnabled(True)

        self.analyze_button.setEnabled(False)
        self.clear_button.setEnabled(False)

        self.show_statistics()

    def enter_view_state(self):
        """
            Växlar vyn till analysläge efter
            genomförd analys.
        """
        self.enable_navigation(True)

        self.competition_combo.setEnabled(False)
        self.season_combo.setEnabled(False)
        self.home_team_combo.setEnabled(False)
        self.away_team_combo.setEnabled(False)

        self.analyze_button.setEnabled(False)
        self.clear_button.setEnabled(True)

    def enable_analyze(self):
        """
        Aktiverar analysknappen.
        """
        self.analyze_button.setEnabled(
            True
        )

        self.clear_button.setEnabled(
            True
        )

    def enable_navigation(self, status):
        """
            Aktiverar eller inaktiverar navigeringsknapparna.
        """
        for button in (
            self.statistics_button,
            self.poisson_button,
            self.probability_button,
            self.odds_button
        ):
            button.setEnabled(
                status
            )

    def clear_analysis(self):
        """
            Tömmer analysens tabeller och lambda-värden.
        """
        tables = (
            self.total_table,
            self.venue_table,
            self.model_table,
            self.h2h_table,
            self.home_poisson_table,
            self.away_poisson_table
        )

        for table in tables:
            table.clearContents()

        self.home_lambda_label.setText(
            "λ = -"
        )

        self.away_lambda_label.setText(
            "λ = -"
        )
