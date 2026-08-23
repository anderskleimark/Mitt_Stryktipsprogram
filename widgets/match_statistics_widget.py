from PySide6.QtWidgets import QLabel, QTableWidgetItem

from misc.base_table_widget import BaseTableWidget
from widgets.base_widget import BaseWidget


class MatchStatisticsWidget(BaseWidget):
    """
        Widget för statistik från en matchanalys.

        Widgeten visar total statistik, hemma-/bortastatistik,
        modellparametrar och statistik från inbördes möten.
    """

    # --------------------------------------------------
    # Tabeller
    # --------------------------------------------------

    TABLE_ROWS = 2

    STATISTICS_COLUMN_COUNT = 7
    MODEL_COLUMN_COUNT = 7
    H2H_COLUMN_COUNT = 6

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
    # Texter
    # --------------------------------------------------

    LABEL_TOTAL = "Totalt"
    LABEL_VENUE = "Hemma/Borta"
    LABEL_MODEL = "Modellparametrar"
    LABEL_H2H = "Inbördes möten"

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

    def __init__(self, parent=None):
        """
            Initierar widgeten.
        """
        super().__init__(parent)
        self._create_layout()

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def _create_layout(self):
        """
            Skapar widgetens layout och statistiktabeller.
        """
        layout = self.create_grid_layout(parent=self)

        self.total_table = self.create_table(
            headers=self.STATISTICS_HEADERS,
            wide_column=self.COLUMN_TEAM
        )

        self.venue_table = self.create_table(
            headers=self.STATISTICS_HEADERS,
            wide_column=self.COLUMN_TEAM
        )

        self.model_table = self.create_table(
            headers=self.MODEL_HEADERS,
            wide_column=self.MODEL_COLUMN_TEAM
        )

        self.h2h_table = self.create_table(
            headers=self.H2H_HEADERS,
            wide_column=self.H2H_COLUMN_TEAM
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

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar statistik från den genomförda
            matchanalysen.
        """
        home = analysis.home_statistics
        away = analysis.away_statistics

        self.fill_table(
            self.total_table,
            (
                self.get_total_statistics_row(home),
                self.get_total_statistics_row(away)
            )
        )

        self.fill_table(
            self.venue_table,
            (
                self.get_home_statistics_row(home),
                self.get_away_statistics_row(away)
            )
        )

        self.fill_table(
            self.model_table,
            (
                self.get_home_model_row(analysis),
                self.get_away_model_row(analysis)
            )
        )

        self.fill_table(
            self.h2h_table,
            self.get_h2h_rows(analysis)
        )

    # --------------------------------------------------
    # Tabellskapande
    # --------------------------------------------------

    def create_table(
        self,
        *,
        headers,
        wide_column
    ):
        """
            Skapar och returnerar en tabell med angivet
            antal kolumner, rubriker och bred kolumn.
        """
        table = BaseTableWidget(
            parent=None,
            readonly=True,
            rowselection=False,
            row_count=self.TABLE_ROWS,
            headers=headers
        )

        table.verticalHeader().setVisible(False)
        table.set_wide_column(wide_column)

        table.set_narrow_columns(
            range(
                wide_column + 1,
                len(headers)
            )
        )

        table.set_no_selection()
        return table

    # --------------------------------------------------
    # Tabelluppdatering
    # --------------------------------------------------

    def fill_table(
        self,
        table,
        table_rows
    ):
        """
        Fyller angiven tabell med de angivna
        statistikraderna.
        """
        table.clearContents()

        for row, values in enumerate(table_rows):
            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self.center_table_columns(table)

    def center_table_columns(
        self,
        table
    ):
        """
            Centrerar tabellens numeriska kolumner.
        """
        for column in range(
            self.COLUMN_MATCHES,
            table.columnCount()
        ):
            table.center_column(column)

    # --------------------------------------------------
    # Statistikrader
    # --------------------------------------------------

    def get_total_statistics_row(
        self,
        statistics
    ):
        """
            Skapar och returnerar en tabellrad med
            lagets totala statistik.
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
            Skapar och returnerar en tabellrad med
            lagets hemmastatistik.
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
        Skapar och returnerar en tabellrad med
        lagets bortastatistik.
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
        Skapar och returnerar modellraden för
        hemmalaget.
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
        Skapar och returnerar modellraden för
        bortalaget.
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
        Skapar och returnerar tabellraderna för
        lagens inbördes möten.
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

    def clear_analysis(self):
        """
        Tömmer statistik från föregående
        matchanalys.
        """
        tables = (
            self.total_table,
            self.venue_table,
            self.model_table,
            self.h2h_table
        )

        for table in tables:
            table.clearContents()
