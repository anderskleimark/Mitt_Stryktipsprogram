from mvc import View

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidgetItem,
    QStackedWidget
)

from misc.base_combo_box import BaseComboBox
from misc.base_table_widget import BaseTableWidget


class MatchAnalysisView(View):

    # --------------------------------------------
    # Konstanter
    # --------------------------------------------

    # Statistiktabeller.
    STATISTICS_ROWS = 2
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

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()

        self.create_header("Matchanalys")
        self.layout.addWidget(self.header)

        # Bygg UI
        self.create_match_selection_widget()
        self.create_analysis_widget()

        self.setLayout(self.layout)

    def create_match_selection_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()

        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Liga"))

        self.competition_combo = BaseComboBox()
        layout.addWidget(self.competition_combo, 2)

        layout.addWidget(QLabel("Säsong"))

        self.season_combo = BaseComboBox()
        layout.addWidget(self.season_combo, 1)

        layout.addWidget(QLabel("Hemmalag"))

        self.home_team_combo = BaseComboBox()
        layout.addWidget(self.home_team_combo, 2)

        layout.addWidget(QLabel("Bortalag"))

        self.away_team_combo = BaseComboBox()
        layout.addWidget(self.away_team_combo, 2)

        self.analyze_button = QPushButton("Analysera")
        layout.addWidget(self.analyze_button)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        widget.setLayout(layout)

        self.layout.addWidget(widget)
        self.layout.addWidget(separator)

    def create_analysis_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Stackad analysyta
        self.analysis_stack = QStackedWidget()

        self.create_statistics_page()
        self.create_poisson_page()
        self.create_probability_page()
        self.create_odds_page()

        layout.addWidget(self.analysis_stack, 1)

        # Navigering längst ned
        self.create_navigation()

        layout.addWidget(self.navigation_widget)
        widget.setLayout(layout)

        self.layout.addWidget(widget)

    def create_statistics_page(self):
        self.statistics_page = QWidget()

        layout = QGridLayout()

        # Fyra små tabeller
        self.total_table = self.create_statistics_table()
        self.venue_table = self.create_statistics_table()
        self.model_table = self.create_model_table()

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

    def create_poisson_page(self):
        self.poisson_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Poisson-analys")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.poisson_page.setLayout(layout)

        self.analysis_stack.addWidget(self.poisson_page)

    def create_probability_page(self):
        self.probability_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Sannolikheter")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.probability_page.setLayout(layout)
        self.analysis_stack.addWidget(self.probability_page)

    def create_odds_page(self):
        self.odds_page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Oddsanalys")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)

        self.odds_page.setLayout(layout)
        self.analysis_stack.addWidget(self.odds_page)

    def create_navigation(self):
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

    def fill_competition_combo(self, competitions: list = []):
        self.competition_combo.blockSignals(True)

        self.competition_combo.clear_with_empty_item()

        for competition in competitions:
            self.competition_combo.addItem(
                competition.name
            )

        self.competition_combo.blockSignals(False)

    def fill_season_combo(self, seasons: list = []):
        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(
                season.name
            )

    def fill_team_combos(self, teams):
        self.home_team_combo.blockSignals(True)
        self.away_team_combo.blockSignals(True)

        self.fill_home_team_combo(teams)
        self.fill_away_team_combo(teams)

        self.home_team_combo.blockSignals(False)
        self.away_team_combo.blockSignals(False)

    def fill_home_team_combo(self, teams):
        self.home_team_combo.clear_with_empty_item()

        for team in teams:
            self.home_team_combo.addItem(
                team.name,
                team
            )

    def fill_away_team_combo(self, teams):
        self.away_team_combo.clear_with_empty_item()

        for team in teams:
            self.away_team_combo.addItem(
                team.name,
                team
            )

    def show_analysis(self, analysis):
        home = analysis.home_statistics
        away = analysis.away_statistics

        self.fill_statistics_table(
            self.total_table,
            [
                [
                    home.team.name,
                    home.matches_played,
                    home.wins,
                    home.draws,
                    home.losses,
                    home.goals_for_against,
                    home.goal_difference
                ],
                [
                    away.team.name,
                    away.matches_played,
                    away.wins,
                    away.draws,
                    away.losses,
                    away.goals_for_against,
                    away.goal_difference
                ]
            ]
        )

        self.fill_statistics_table(
            self.venue_table,
            [
                self.get_home_statistics_row(home),
                self.get_away_statistics_row(away)
            ]
        )

        self.fill_model_table(
            self.model_table,
            [
                [
                    home.team.name,
                    f"{analysis.lambda_home:.2f}",
                    f"{home.home_attack_coefficient:.2f}",
                    f"{home.home_defence_coefficient:.2f}",
                    f"{home.average_home_goals_for:.2f}",
                    f"{home.average_home_goals_against:.2f}",
                    f"{home.recent_form:.2f}"
                ],
                [
                    away.team.name,
                    f"{analysis.lambda_away:.2f}",
                    f"{away.away_attack_coefficient:.2f}",
                    f"{away.away_defence_coefficient:.2f}",
                    f"{away.average_away_goals_for:.2f}",
                    f"{away.average_away_goals_against:.2f}",
                    f"{away.recent_form:.2f}"
                ]
            ]
        )

    def show_statistics(self):
        self.analysis_stack.setCurrentWidget(self.statistics_page)

    def show_poisson(self):
        self.analysis_stack.setCurrentWidget(self.poisson_page)

    def show_probabilities(self):
        self.analysis_stack.setCurrentWidget(self.probability_page)

    def show_odds(self):
        self.analysis_stack.setCurrentWidget(self.odds_page)

    def create_statistics_table(self):
        table = BaseTableWidget(
            readonly=True,
            rowselection=False,
            rows=self.STATISTICS_ROWS,
            cols=self.STATISTICS_COLUMNS
        )

        table.setHorizontalHeaderLabels(self.STATISTICS_HEADERS)

        table.verticalHeader().setVisible(False)
        table.set_wide_column(self.COLUMN_TEAM)

        table.set_narrow_columns(
            range(
                self.COLUMN_MATCHES,
                self.STATISTICS_COLUMNS
            )
        )
        table.set_no_selection()

        return table

    def create_model_table(self):
        table = BaseTableWidget(
            readonly=True,
            rowselection=False,
            rows=self.STATISTICS_ROWS,
            cols=self.MODEL_COLUMNS
        )

        table.setHorizontalHeaderLabels(self.MODEL_HEADERS)

        table.verticalHeader().setVisible(False)
        table.set_wide_column(self.MODEL_COLUMN_TEAM)
        table.set_narrow_columns(
            range(
                self.MODEL_COLUMN_LAMBDA,
                self.MODEL_COLUMNS
            )
        )

        return table

    def center_table_columns(self, table):
        for column in range(
            self.COLUMN_MATCHES,
            table.columnCount()
        ):
            table.center_column(column)

    def fill_statistics_table(self, table, table_rows):
        for row, values in enumerate(table_rows):
            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

        self.center_table_columns(table)

    def fill_model_table(self, table, rows):
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

        self.center_table_columns(table)

    def get_total_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.matches_played,
            statistics.wins,
            statistics.draws,
            statistics.losses,
            statistics.goals_for_against,
            statistics.goal_difference
        ]

    def get_home_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.home_matches_played,
            statistics.home_wins,
            statistics.home_draws,
            statistics.home_losses,
            statistics.home_goals_for_against,
            statistics.home_goal_difference
        ]

    def get_away_statistics_row(self, statistics):
        return [
            statistics.team.name,
            statistics.away_matches_played,
            statistics.away_wins,
            statistics.away_draws,
            statistics.away_losses,
            statistics.away_goals_for_against,
            statistics.away_goal_difference
        ]
