from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from misc.base_combo_box import BaseComboBox
from misc.base_table_widget import BaseTableWidget
from mvc import View


class MatchAnalysisView(View):
    """
    Klass som visar och presenterar analys av en fotbollsmatch.
    """
    # --------------------------------------------
    # Konstanter
    # --------------------------------------------

    # Tabeller.
    TABLE_ROWS = 2
    STATISTICS_COLUMNS = 7
    MODEL_COLUMNS = 7

    COLUMN_TEAM = 0
    COLUMN_MATCHES = 1
    COLUMN_WINS = 2
    COLUMN_DRAWS = 3
    COLUMN_LOSSES = 4
    COLUMN_GOALS = 5
    COLUMN_GOAL_DIFFERENCE = 6

    MODEL_COLUMN_TEAM = 0
    MODEL_COLUMN_LAMBDA = 1
    MODEL_COLUMN_ATTACK = 2
    MODEL_COLUMN_DEFENCE = 3
    MODEL_COLUMN_AVG_GOALS_FOR = 4
    MODEL_COLUMN_AVG_GOALS_AGAINST = 5
    MODEL_COLUMN_FORM = 6

    STATISTICS_HEADERS = [
        "Lag",
        "Sp",
        "V",
        "O",
        "F",
        "Mål",
        "Δ"
    ]

    MODEL_HEADERS = [
        "Lag",
        "λ",
        "Attack",
        "Försvar",
        "GF/M",
        "GA/M",
        "Form"
    ]

    BUTTON_FIXED_WIDTH = 110

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

        # Widgetar och knappar
        self.navigation_widget = None
        self.statistics_button = None
        self.poisson_button = None
        self.probability_button = None
        self.odds_button = None

        self.layout = self.create_layout()

        self.create_header("Matchanalys")
        self.layout.addWidget(self.header)

        # Bygg UI
        self._create_match_selection_widget()
        self._create_analysis_widget()

        self.setLayout(self.layout)

    # Funktion som skapar widgeten för val av liga, säsong och lag.
    def _create_match_selection_widget(self):
        widget = QWidget()
        layout = QGridLayout()

        layout.setContentsMargins(0, 20, 0, 20)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        # Combo-boxar
        self.competition_combo = BaseComboBox()
        self.season_combo = BaseComboBox()
        self.home_team_combo = BaseComboBox()
        self.away_team_combo = BaseComboBox()

        # Knappar
        self.clear_button = QPushButton("Rensa")
        self.analyze_button = QPushButton("Analysera")

        self.clear_button.setFixedWidth(self.BUTTON_FIXED_WIDTH)
        self.analyze_button.setFixedWidth(self.BUTTON_FIXED_WIDTH)

        self.analyze_button.setDefault(True)
        self.analyze_button.setAutoDefault(True)

        # -----------------------------
        # Rad 1
        # -----------------------------
        layout.addWidget(QLabel("Liga"), 0, 0)
        layout.addWidget(self.competition_combo, 0, 1)

        layout.addWidget(QLabel("Säsong"), 0, 2)
        layout.addWidget(self.season_combo, 0, 3)

        layout.addWidget(self.clear_button, 0, 4)

        # -----------------------------
        # Rad 2
        # -----------------------------
        layout.addWidget(QLabel("Hemmalag"), 1, 0)
        layout.addWidget(self.home_team_combo, 1, 1)

        layout.addWidget(QLabel("Bortalag"), 1, 2)
        layout.addWidget(self.away_team_combo, 1, 3)

        layout.addWidget(self.analyze_button, 1, 4)

        # Ge comboboxarna plats
        layout.setColumnStretch(1, 3)
        layout.setColumnStretch(3, 3)

        widget.setLayout(layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.layout.addWidget(widget)
        self.layout.addWidget(separator)

    # Funktion som skapar analysytan och dess navigering.
    def _create_analysis_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Stackad analysyta
        self.analysis_stack = QStackedWidget()

        self._create_statistics_page()
        self._create_poisson_page()
        self._create_probability_page()
        self._create_odds_page()

        layout.addWidget(self.analysis_stack, 1)

        # Navigering längst ned
        self._create_navigation()

        layout.addWidget(self.navigation_widget)
        widget.setLayout(layout)

        self.layout.addWidget(widget)

    # Funktion som skapar sidan med statistiktabeller.
    def _create_statistics_page(self):
        self.statistics_page = QWidget()

        layout = QGridLayout()

        # Fyra små tabeller
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

        # Övre raden
        layout.addWidget(QLabel("Totalt"), 1, 0)
        layout.addWidget(QLabel("Hemma/Borta"), 1, 1)

        layout.addWidget(self.total_table, 2, 0)
        layout.addWidget(self.venue_table, 2, 1)

        # Nedre raden
        layout.addWidget(QLabel("Modellparametrar"), 3, 0)
        layout.addWidget(self.model_table, 4, 0)

        self.statistics_page.setLayout(layout)
        self.analysis_stack.addWidget(self.statistics_page)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

    # Funktion som skapar sidan för poisson-analys.
    def _create_poisson_page(self):
        self.poisson_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Poisson-analys")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.poisson_page.setLayout(layout)

        self.analysis_stack.addWidget(self.poisson_page)

    # Funktion som skapar sidan med sannolikheter.
    def _create_probability_page(self):
        self.probability_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Sannolikheter")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.probability_page.setLayout(layout)
        self.analysis_stack.addWidget(self.probability_page)

    # Funktion som skapar sidan med oddsanalys.
    def _create_odds_page(self):
        self.odds_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Oddsanalys")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.odds_page.setLayout(layout)
        self.analysis_stack.addWidget(self.odds_page)

    # Funktion som skapar navigeringsknapparna.
    def _create_navigation(self):
        self.navigation_widget = QWidget()

        layout = QHBoxLayout()

        self.statistics_button = QPushButton("Statistik")
        self.poisson_button = QPushButton("Poisson")
        self.probability_button = QPushButton("Sannolikhet")
        self.odds_button = QPushButton("Odds")

        layout.addWidget(self.statistics_button)
        layout.addWidget(self.poisson_button)
        layout.addWidget(self.probability_button)
        layout.addWidget(self.odds_button)

        self.navigation_widget.setLayout(layout)

    def fill_competition_combo(self, competitions: list = None):
        """
            Funktion som fyller listan med tillgängliga ligor.
        """
        if competitions is None:
            competitions = []

        self.competition_combo.blockSignals(True)
        self.competition_combo.clear_with_empty_item()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.name
            )

        self.competition_combo.blockSignals(False)

    def fill_season_combo(self, seasons: list = None):
        """
            Funktion som fyller listan med tillgängliga ligor.
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
            Funktion som fyller listorna för både hemma- och bortalagen.
        """
        self.home_team_combo.blockSignals(True)
        self.away_team_combo.blockSignals(True)

        self.fill_home_team_combo(teams)
        self.fill_away_team_combo(teams)

        self.home_team_combo.blockSignals(False)
        self.away_team_combo.blockSignals(False)

    def fill_home_team_combo(self, teams=None):
        """
            Funktion som fyller listan med hemmalag.
        """
        if teams is None:
            teams = []
        self.home_team_combo.clear_with_empty_item()

        for team in teams:
            self.home_team_combo.addItem(
                team.name,
                team
            )

    def fill_away_team_combo(self, teams=None):
        """
            Funktion som fyller listan med bortalag.
        """
        if teams is None:
            teams = []
        self.away_team_combo.clear_with_empty_item()

        for team in teams:
            self.away_team_combo.addItem(
                team.name,
                team
            )

    def show_analysis(self, analysis):
        """
            Funktion som visar resultatet av en matchanalys.
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
                self._get_away_model_row(analysis),
            ]
        )

    def show_statistics(self):
        """
            Funktion som visar sidan med statistik.
        """
        self.analysis_stack.setCurrentWidget(self.statistics_page)

    def show_poisson(self):
        """
            Funktion som visar sidan med poisson-analys.
        """
        self.analysis_stack.setCurrentWidget(self.poisson_page)

    def show_probabilities(self):
        """
            Funktion som visar sidan med sannolikheter.
        """
        self.analysis_stack.setCurrentWidget(self.probability_page)

    def show_odds(self):
        """
            Funktion som visar sidan med odds.
        """
        self.analysis_stack.setCurrentWidget(self.odds_page)

    # Funktion som skapar en tabell med angivna kolumner och rubriker.
    def _create_table(self, columns, headers, wide_column):
        table = BaseTableWidget(
            readonly=True,
            rowselection=False,
            rows=self.TABLE_ROWS,
            cols=columns
        )

        table.setHorizontalHeaderLabels(headers)

        table.verticalHeader().setVisible(False)
        table.set_wide_column(wide_column)

        table.set_narrow_columns(
            range(wide_column + 1, columns)
        )

        table.set_no_selection()
        return table

    # Funktion som centrerar tabellens numeriska kolumner.
    def _center_table_columns(self, table):
        for column in range(
            self.COLUMN_MATCHES,
            table.columnCount()
        ):
            table.center_column(column)

    # Funktion som fyller en tabell med data.
    def _fill_table(self, table, table_rows):
        for row, values in enumerate(table_rows):
            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

        self._center_table_columns(table)

    # Funktion som rReturnerar en rad med lagets totala statistik.
    def _get_total_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.matches_played,
            statistics.wins,
            statistics.draws,
            statistics.losses,
            statistics.goals_for_against,
            statistics.goal_difference
        ]

    # Funktion som returnerar en rad med hemmastatistik.
    def _get_home_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.home_matches_played,
            statistics.home_wins,
            statistics.home_draws,
            statistics.home_losses,
            statistics.home_goals_for_against,
            statistics.home_goal_difference
        ]

    # Funktion som returnerar en rad med bortastatistik.
    def _get_away_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.away_matches_played,
            statistics.away_wins,
            statistics.away_draws,
            statistics.away_losses,
            statistics.away_goals_for_against,
            statistics.away_goal_difference
        ]

    # Funktion som returnerar en rad med modellparametrar för hemmalaget.
    def _get_home_model_row(self, analysis):
        statistics = analysis.home_statistics

        return [
            statistics.team.name,
            f"{analysis.lambda_home:.2f}",
            f"{statistics.home_attack_coefficient:.2f}",
            f"{statistics.home_defence_coefficient:.2f}",
            f"{statistics.average_home_goals_for:.2f}",
            f"{statistics.average_home_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        ]

    # Funktion som returnerar en rad med modellparametrar för bortalaget.
    def _get_away_model_row(self, analysis):
        statistics = analysis.away_statistics

        return [
            statistics.team.name,
            f"{analysis.lambda_away:.2f}",
            f"{statistics.away_attack_coefficient:.2f}",
            f"{statistics.away_defence_coefficient:.2f}",
            f"{statistics.average_away_goals_for:.2f}",
            f"{statistics.average_away_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        ]

    def enter_pre_analyze_state(self):
        """
            Funktion som återställer vyn inför en ny matchanalys.
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
            Funktion som växlar vyn till analysläge efter en genomförd analys.
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
            Funktion som aktiverar knappen för att analysera matchen.
        """
        self.analyze_button.setEnabled(True)
        self.clear_button.setEnabled(True)

    # Funktion för att aktivera eller deaktiver navigationen.

    def enable_navigation(self, status):
        """
            Funktion som aktiverar eller inaktiverar navigeringsknapparna.
        """
        for button in (
            self.statistics_button,
            self.poisson_button,
            self.probability_button,
            self.odds_button
        ):
            button.setEnabled(status)

    def clear_analysis(self):
        """
            Funktion som tömmer analysens tabeller.
        """
        tables = [
            self.total_table,
            self.venue_table,
            self.model_table
        ]

        for table in tables:
            table.clearContents()
