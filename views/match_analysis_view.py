from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QGridLayout, QHeaderView, QLabel,
                               QStackedWidget, QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import (DixonColesButton, OddsButton, ProbabilityButton,
                          StatisticButton)
from mvc import View
from widgets.match_selection_widget import MatchSelectionWidget


class MatchAnalysisView(View):
    """
        Vy för att visa och hantera analys av en fotbollsmatch.

        Vyn innehåller val av tävling, säsong
        och lag samt separata analyssidor för
        statistik, Dixon-Coles, sannolikheter
        och odds.
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
    # Tabeller
    # --------------------------------------------------

    TABLE_ROWS = 2

    STATISTICS_COLUMN_COUNT = 7
    MODEL_COLUMN_COUNT = 7
    H2H_COLUMN_COUNT = 6

    POISSON_ROW_COUNT = 6
    POISSON_COLUMN_COUNT = 2

    SCORE_COLUMN_COUNT = 2
    SCORE_ROW_COUNT = 5

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
    # Tabellrubriker
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

    SCORE_HEADERS = (
        "Resultat",
        "Sannolikhet"
    )

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Matchanalys"

    LABEL_HOME_TEAM = "Hemmalag"
    LABEL_AWAY_TEAM = "Bortalag"

    LABEL_TOTAL = "Totalt"
    LABEL_VENUE = "Hemma/Borta"
    LABEL_MODEL = "Modellparametrar"
    LABEL_H2H = "Inbördes möten"

    LABEL_ODDS = "Oddsanalys"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    ANALYSIS_PAGE_SPACING = 1
    NAVIGATION_SPACING = None

    def __init__(self):
        """
            Initierar vyn och skapar matchval, analyssidor, navigering och
            signalanslutningar.
        """
        super().__init__()

        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.match_selection_widget = MatchSelectionWidget()
        self.layout.addWidget(
            self.match_selection_widget
        )

        self.create_separator()
        self.create_analysis_widget()
        self.create_navigation_widget()

        self.add_bottom_panel(self.navigation_widget)
        self.setLayout(self.layout)
        self._setup_signals()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Vidarebefordrar signaler från underliggande widgetar genom
            vyklassens egna signaler.
        """
        self.match_selection_widget.competition_changed.connect(
            self.competition_changed.emit)

        self.match_selection_widget.season_changed.connect(
            self.season_changed.emit
        )

        self.match_selection_widget.home_team_changed.connect(
            self.home_team_changed.emit
        )

        self.match_selection_widget.away_team_changed.connect(
            self.away_team_changed.emit
        )

        self.match_selection_widget.analyze_clicked.connect(
            self.analyze_clicked.emit
        )

        self.match_selection_widget.clear_clicked.connect(
            self.clear_clicked.emit
        )

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_separator(self):
        """
            Skapar den horisontella avskiljaren mellan matchvalet och analysytan.
        """
        self.separator = QFrame()

        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(self.separator)

    def create_analysis_widget(self):
        """
            Skapar analysytan och dess underliggande analyssidor.
        """
        self.analysis_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.analysis_widget,
            spacing=self.ANALYSIS_PAGE_SPACING
        )

        self.analysis_stack = QStackedWidget()

        self.create_statistics_page()
        self.create_dixon_coles_page()
        self.create_probability_page()
        self.create_odds_page()

        layout.addWidget(self.analysis_stack)

        self.layout.addWidget(
            self.analysis_widget,
            stretch=self.FULL_STRETCH
        )

    def create_statistics_page(self):
        """
            Skapar statistiksidan.

            Sidan innehåller tabeller för total
            statistik, hemma-/bortastatistik,
            modellparametrar och inbördes möten.
        """
        self.statistics_page = QWidget()

        layout = QGridLayout(self.statistics_page)
        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.total_table = self.create_table(
            self.STATISTICS_COLUMN_COUNT,
            self.STATISTICS_HEADERS,
            self.COLUMN_TEAM
        )

        self.venue_table = self.create_table(
            self.STATISTICS_COLUMN_COUNT,
            self.STATISTICS_HEADERS,
            self.COLUMN_TEAM
        )

        self.model_table = self.create_table(
            self.MODEL_COLUMN_COUNT,
            self.MODEL_HEADERS,
            self.MODEL_COLUMN_TEAM
        )

        self.h2h_table = self.create_table(
            self.H2H_COLUMN_COUNT,
            self.H2H_HEADERS,
            self.H2H_COLUMN_TEAM
        )

        layout.addWidget(
            QLabel(self.LABEL_TOTAL),
            0,
            0
        )

        layout.addWidget(
            QLabel(self.LABEL_VENUE),
            0,
            1
        )

        layout.addWidget(
            self.total_table,
            1,
            0
        )

        layout.addWidget(
            self.venue_table,
            1,
            1
        )

        layout.addWidget(
            QLabel(self.LABEL_MODEL),
            2,
            0
        )

        layout.addWidget(
            QLabel(self.LABEL_H2H),
            2,
            1
        )

        layout.addWidget(
            self.model_table,
            3,
            0
        )

        layout.addWidget(
            self.h2h_table,
            3,
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

        self.analysis_stack.addWidget(self.statistics_page)

    def create_dixon_coles_page(self):
        """
            Skapar sidan för Dixon-Coles-analys.

            Sidan visar rho-parametern samt
            Poissonfördelningarna för hemma-
            och bortalaget.
        """
        self.dixon_coles_page = QWidget()

        layout = self.create_vertical_layout(
            parent=self.dixon_coles_page,
            spacing=None
        )

        self.rho_label = QLabel("ρ = -")

        self.rho_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.rho_label)
        distributions_widget = QWidget()

        distributions_layout = (
            self.create_horizontal_layout(
                parent=distributions_widget,
                spacing=None
            )
        )

        self.create_home_poisson_widget()
        self.create_away_poisson_widget()

        distributions_layout.addWidget(self.home_poisson_widget)
        distributions_layout.addWidget(self.away_poisson_widget)

        layout.addWidget(distributions_widget)
        self.analysis_stack.addWidget(self.dixon_coles_page)

    def create_home_poisson_widget(self):
        """
            Skapar widgeten med hemmalagets lambda och Poissonfördelning.
        """
        self.home_poisson_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.home_poisson_widget,
            spacing=1
        )

        label = QLabel(self.LABEL_HOME_TEAM)

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        self.home_lambda_label = QLabel("λ = -")
        self.home_lambda_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.home_lambda_label)
        self.home_poisson_table = self.create_poisson_table()

        layout.addWidget(self.home_poisson_table)

    def create_away_poisson_widget(self):
        """
            Skapar widgeten med bortalagets lambda och Poissonfördelning.
        """
        self.away_poisson_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.away_poisson_widget,
            spacing=1
        )

        label = QLabel(self.LABEL_AWAY_TEAM)

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        self.away_lambda_label = QLabel("λ = -")
        self.away_lambda_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.away_lambda_label)

        self.away_poisson_table = self.create_poisson_table()
        layout.addWidget(self.away_poisson_table)

    def create_probability_page(self):
        """
            Skapar sannolikhetssidan.

            Sidan visar sannolikheter för 1X2,
            över/under 2.5 mål, båda lagen gör
            mål samt de mest sannolika resultaten.
        """
        self.probability_page = QWidget()

        layout = self.create_vertical_layout(
            parent=self.probability_page,
            spacing=None
        )

        probability_widget = QWidget()
        probability_layout = QGridLayout(probability_widget)
        probability_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        probability_layout.setHorizontalSpacing(10)
        probability_layout.setVerticalSpacing(10)

        # 1X2
        self.probability_1_label = QLabel("1: -")

        self.probability_x_label = QLabel("X: -")
        self.probability_2_label = QLabel("2: -")

        # Över/under 2.5 mål
        self.probability_over_25_label = QLabel("Över 2.5: -")
        self.probability_under_25_label = QLabel("Under 2.5: -")

        # BTTS
        self.probability_btts_label = QLabel("Båda lagen gör mål: -")

        probability_layout.addWidget(
            self.probability_1_label,
            0,
            0,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        probability_layout.addWidget(
            self.probability_x_label,
            0,
            1,
            Qt.AlignmentFlag.AlignCenter
        )

        probability_layout.addWidget(
            self.probability_2_label,
            0,
            2,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        probability_layout.addWidget(
            self.probability_over_25_label,
            1,
            0,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        probability_layout.addWidget(
            self.probability_under_25_label,
            1,
            2,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        probability_layout.addWidget(
            self.probability_btts_label,
            2,
            0,
            1,
            3,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        for column in range(3):
            probability_layout.setColumnStretch(
                column,
                1
            )

        layout.addWidget(probability_widget)

        self.score_table = BaseTableWidget(
            True,
            False,
            self.SCORE_COLUMN_COUNT,
            self.SCORE_ROW_COUNT
        )

        self.score_table.setHorizontalHeaderLabels(self.SCORE_HEADERS)
        self.score_table.verticalHeader().setVisible(False)

        header = self.score_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.score_table.set_no_selection()

        layout.addWidget(self.score_table)
        self.analysis_stack.addWidget(self.probability_page)

    def create_odds_page(self):
        """
            Skapar sidan för oddsanalys.
        """
        self.odds_page = QWidget()

        layout = self.create_vertical_layout(
            parent=self.odds_page,
            spacing=None
        )

        label = QLabel(self.LABEL_ODDS)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        self.analysis_stack.addWidget(self.odds_page)

    def create_navigation_widget(self):
        """
            Skapar navigeringspanelen för växling mellan analyssidorna.
        """
        self.navigation_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.navigation_widget,
            spacing=self.NAVIGATION_SPACING
        )

        self.statistics_button = StatisticButton()

        layout.addWidget(self.statistics_button)

        self.dixon_coles_button = DixonColesButton()
        layout.addWidget(self.dixon_coles_button)

        self.probability_button = ProbabilityButton()

        layout.addWidget(self.probability_button)

        self.odds_button = OddsButton()

        layout.addWidget(self.odds_button)

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_statistics(self):
        """
            Visar statistiksidan.
        """
        self.analysis_stack.setCurrentWidget(self.statistics_page)

    def show_dixon_coles(self):
        """
            Visar Dixon-Coles-sidan.
        """
        self.analysis_stack.setCurrentWidget(self.dixon_coles_page)

    def show_probabilities(self):
        """
            Visar sannolikhetssidan.
        """
        self.analysis_stack.setCurrentWidget(self.probability_page)

    def show_odds(self):
        """
            Visar oddssidan.
        """
        self.analysis_stack.setCurrentWidget(self.odds_page)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar resultatet från en genomförd matchanalys i samtliga analyssidor.
        """
        home = analysis.home_statistics
        away = analysis.away_statistics

        # Total statistik
        self.fill_table(
            self.total_table,
            [
                self.get_total_statistics_row(home),
                self.get_total_statistics_row(away)
            ]
        )

        # Hemma-/bortastatistik
        self.fill_table(
            self.venue_table,
            [
                self.get_home_statistics_row(home),
                self.get_away_statistics_row(away)
            ]
        )

        # Modellparametrar
        self.fill_table(
            self.model_table,
            [
                self.get_home_model_row(analysis),
                self.get_away_model_row(analysis)
            ]
        )

        # Inbördes möten
        self.fill_table(
            self.h2h_table,
            self.get_h2h_rows(analysis)
        )

        # Poissonfördelningar
        self.fill_poisson_table(
            self.home_poisson_table,
            analysis.home_poisson
        )

        self.fill_poisson_table(
            self.away_poisson_table,
            analysis.away_poisson
        )

        # Lambda
        self.home_lambda_label.setText(f"λ = {analysis.lambda_home:.2f}")
        self.away_lambda_label.setText(f"λ = {analysis.lambda_away:.2f}")

        # Dixon-Coles rho
        self.rho_label.setText(f"ρ = {analysis.rho:.3f}")

        # 1X2
        self.probability_1_label.setText(f"1: {analysis.probability_1:.1%}")

        self.probability_x_label.setText(f"X: {analysis.probability_x:.1%}")
        self.probability_2_label.setText(f"2: {analysis.probability_2:.1%}")

        # Över/under 2.5 mål
        self.probability_over_25_label.setText(
            f"Över 2.5: "
            f"{analysis.probability_over_25:.1%}"
        )

        self.probability_under_25_label.setText(
            f"Under 2.5: "
            f"{analysis.probability_under_25:.1%}"
        )

        # Båda lagen gör mål
        self.probability_btts_label.setText(
            f"Båda lagen gör mål: "
            f"{analysis.probability_btts:.1%}"
        )

        # Mest sannolika resultat
        self.fill_score_table(analysis.most_likely_scores)

    # --------------------------------------------------
    # Tabellskapande
    # --------------------------------------------------

    def create_table(
        self,
        columns,
        headers,
        wide_column
    ):
        """
            Skapar och returnerar en tabell med angivet antal kolumner,
            rubriker och bred kolumn.
        """
        table = BaseTableWidget(
            True,
            False,
            columns,
            self.TABLE_ROWS
        )

        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)

        table.set_wide_column(wide_column)

        table.set_narrow_columns(
            range(
                wide_column + 1,
                columns
            )
        )

        table.set_no_selection()

        return table

    def create_poisson_table(self):
        """
            Skapar och returnerar en tabell för en Poissonfördelning.
        """
        table = BaseTableWidget(
            True,
            False,
            self.POISSON_COLUMN_COUNT,
            self.POISSON_ROW_COUNT
        )

        table.setHorizontalHeaderLabels(self.POISSON_HEADERS)
        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.set_no_selection()

        return table

    # --------------------------------------------------
    # Tabelluppdatering
    # --------------------------------------------------

    def center_table_columns(
        self,
        table
    ):
        """
            Centrerar tabellens numeriska
            kolumner.
        """
        for column in range(
            self.COLUMN_MATCHES,
            table.columnCount()
        ):
            table.center_column(
                column
            )

    def fill_table(
        self,
        table,
        table_rows
    ):
        """
            Fyller angiven tabell med de angivna raderna.
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

        self.center_table_columns(table)

    def fill_poisson_table(
        self,
        table,
        distribution
    ):
        """
            Fyller en Poisson-tabell med
            målantal och motsvarande
            sannolikheter.
        """
        table.clearContents()

        if not distribution:
            return

        last_index = len(distribution) - 1

        for goals, probability in enumerate(distribution):
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

    def fill_score_table(
        self,
        scores
    ):
        """
            Fyller resultattabellen med de mest
            sannolika exakta matchresultaten.
        """
        self.score_table.clearContents()

        self.score_table.setRowCount(len(scores))

        for row, (
            home_goals,
            away_goals,
            probability
        ) in enumerate(scores):
            self.score_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    f"{home_goals}–{away_goals}"
                )
            )

            self.score_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{probability:.1%}".replace(
                        "%",
                        " %"
                    )
                )
            )

        self.score_table.center_column(0)
        self.score_table.center_column(1)

    # --------------------------------------------------
    # Statistikrader
    # --------------------------------------------------

    def get_total_statistics_row(
        self,
        statistics
    ):
        """
            Skapar och returnerar en tabellrad
            med lagets totala statistik.
        """
        return (
            statistics.team.display_name,
            statistics.matches_played,
            statistics.wins,
            statistics.draws,
            statistics.losses,
            statistics.goals_for_against,
            statistics.goal_difference
        )

    def get_home_statistics_row(
        self,
        statistics
    ):
        """
            Skapar och returnerar en tabellrad med lagets hemmastatistik.
        """
        return (
            statistics.team.display_name,
            statistics.home_matches_played,
            statistics.home_wins,
            statistics.home_draws,
            statistics.home_losses,
            statistics.home_goals_for_against,
            statistics.home_goal_difference
        )

    def get_away_statistics_row(
        self,
        statistics
    ):
        """
            Skapar och returnerar en tabellrad med lagets bortastatistik.
        """
        return (
            statistics.team.display_name,
            statistics.away_matches_played,
            statistics.away_wins,
            statistics.away_draws,
            statistics.away_losses,
            statistics.away_goals_for_against,
            statistics.away_goal_difference
        )

    def get_home_model_row(
        self,
        analysis
    ):
        """
            Skapar och returnerar modellraden för hemmalaget.
        """
        statistics = analysis.home_statistics

        return (
            statistics.team.display_name,
            f"{analysis.lambda_home:.2f}",
            f"{statistics.home_attack_coefficient:.2f}",
            f"{1 / statistics.home_defence_coefficient:.2f}",
            f"{statistics.average_home_goals_for:.2f}",
            f"{statistics.average_home_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        )

    def get_away_model_row(
        self,
        analysis
    ):
        """
            Skapar och returnerar modellraden för bortalaget.
        """
        statistics = analysis.away_statistics

        return (
            statistics.team.display_name,
            f"{analysis.lambda_away:.2f}",
            f"{statistics.away_attack_coefficient:.2f}",
            f"{1 / statistics.away_defence_coefficient:.2f}",
            f"{statistics.average_away_goals_for:.2f}",
            f"{statistics.average_away_goals_against:.2f}",
            f"{statistics.recent_form:.2f}"
        )

    def get_h2h_rows(
        self,
        analysis
    ):
        """
            Skapar och returnerar tabellraderna
            för lagens inbördes möten.
        """
        h2h = analysis.h2h_statistics

        return (
            (
                analysis.home_statistics.team.display_name,
                h2h.matches,
                h2h.home_wins,
                h2h.home_draws,
                h2h.home_losses,
                h2h.home_score
            ),
            (
                analysis.away_statistics.team.display_name,
                h2h.matches,
                h2h.away_wins,
                h2h.away_draws,
                h2h.away_losses,
                h2h.away_score
            )
        )

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def enter_pre_analyze_state(self):
        """
            Återställer vyn inför en ny matchanalys.

            Tidigare analysresultat och val
            rensas och navigeringen inaktiveras.
        """
        self.clear_analysis()
        self.enable_navigation(False)

        self.set_competition_combo_status(True)
        self.set_season_combo_status(True)
        self.set_home_team_combo_status(True)
        self.set_away_team_combo_status(True)

        self.set_analyze_button_status(False)
        self.set_clear_button_status(False)

        self.reset_match_selection()

        self.show_statistics()

    def enter_view_state(self):
        """
            Växlar vyn till läget efter en
            genomförd analys.

            Navigeringen och rensningsknappen
            aktiveras.
        """
        self.enable_navigation(True)
        self.set_clear_button_status(True)

    def enable_navigation(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            samtliga navigeringsknappar.
        """
        buttons = (
            self.statistics_button,
            self.dixon_coles_button,
            self.probability_button,
            self.odds_button
        )

        for button in buttons:
            button.setEnabled(status)

    def clear_analysis(self):
        """
            Tömmer samtliga resultat från föregående matchanalys.
        """
        tables = (
            self.total_table,
            self.venue_table,
            self.model_table,
            self.h2h_table,
            self.home_poisson_table,
            self.away_poisson_table,
            self.score_table
        )

        for table in tables:
            table.clearContents()

        # Lambda
        self.home_lambda_label.setText("λ = -")
        self.away_lambda_label.setText("λ = -")

        # Dixon-Coles
        self.rho_label.setText("ρ = -")

        # 1X2
        self.probability_1_label.setText("1: -")
        self.probability_x_label.setText("X: -")
        self.probability_2_label.setText("2: -")

        # Över/under 2.5 mål
        self.probability_over_25_label.setText("Över 2.5: -")
        self.probability_under_25_label.setText("Under 2.5: -")

        # Båda lagen gör mål
        self.probability_btts_label.setText("Båda lagen gör mål: -")

    # --------------------------------------------------
    # Delegationsmetoder - innehåll
    # --------------------------------------------------

    def fill_competition_combo(
        self,
        competitions=None
    ):
        """
            Fyller tävlingslistan i matchvalswidgeten.
        """
        self.match_selection_widget.fill_competition_combo(competitions)

    def fill_season_combo(
        self,
        seasons=None
    ):
        """
            Fyller säsongslistan i matchvalswidgeten.
        """
        self.match_selection_widget.fill_season_combo(seasons)

    def fill_team_combos(
        self,
        teams
    ):
        """
            Fyller både hemma- och bortalagslistan.
        """
        self.match_selection_widget.fill_team_combos(teams)

    def fill_home_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med hemmalag.
        """
        self.match_selection_widget.fill_home_team_combo(teams)

    def fill_away_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med bortalag.
        """
        self.match_selection_widget.fill_away_team_combo(teams)

    # --------------------------------------------------
    # Delegationsmetoder - status
    # --------------------------------------------------

    def set_competition_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            tävlingslistan.
        """
        self.match_selection_widget.set_competition_combo_status(status)

    def set_season_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            säsongslistan.
        """
        self.match_selection_widget.set_season_combo_status(status)

    def set_home_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            hemmalagslistan.
        """
        self.match_selection_widget.set_home_team_combo_status(status)

    def set_away_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverarbortalagslistan.
        """
        self.match_selection_widget.set_away_team_combo_status(status)

    def set_analyze_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar analysknappen.
        """
        self.match_selection_widget.set_analyze_button_status(status)

    def set_clear_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar rensningsknappen.
        """
        self.match_selection_widget.set_clear_button_status(status)

    # --------------------------------------------------
    # Delegationsmetoder - val
    # --------------------------------------------------

    def get_selected_competition_row(self):
        """
            Returnerar index för vald tävling.

            Returnerar -1 om ingen tävling är vald.
        """
        return (
            self.match_selection_widget
            .get_selected_competition_row()
        )

    def get_selected_season_row(self):
        """
            Returnerar index för vald säsong.

            Returnerar -1 om ingen säsong
            är vald.
        """
        return self.match_selection_widget.get_selected_season_row()

    def get_selected_home_team(self):
        """
            Returnerar det valda hemmalagets
            Team-objekt.

            Returnerar None om inget hemmalag
            är valt.
        """
        return self.match_selection_widget.get_selected_home_team()

    def get_selected_away_team(self):
        """
            Returnerar det valda bortalagets
            Team-objekt.

            Returnerar None om inget bortalag
            är valt.
        """
        return self.match_selection_widget.get_selected_away_team()

    def reset_match_selection(self):
        """
            Återställer samtliga val i
            matchvalswidgeten.
        """
        self.match_selection_widget.reset()
