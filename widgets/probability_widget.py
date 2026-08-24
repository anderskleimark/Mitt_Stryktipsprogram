from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QLabel, QTableWidgetItem

from misc.base_table_widget import BaseTableWidget
from widgets.base_widget import BaseWidget


class ProbabilityWidget(BaseWidget):
    """
        Widget för att visa beräknade matchsannolikheter.

        Widgeten visar sannolikheter för 1X2, över/under 2.5 mål, båda lagen gör mål
        samt de mest sannolika slutresultaten.
    """

    # --------------------------------------------------
    # Tabeller
    # --------------------------------------------------

    SCORE_ROW_COUNT = 5

    # --------------------------------------------------
    # Tabellrubriker
    # --------------------------------------------------

    SCORE_HEADERS = (
        "Resultat",
        "Sannolikhet"
    )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    GRID_HORIZONTAL_SPACING = 10
    GRID_VERTICAL_SPACING = 10
    GRID_COLUMN_COUNT = 3

    def __init__(self):
        """
            Initierar sannolikhetswidgeten.
        """
        super().__init__()

        self.create_widgets()
        self.create_layout()

        self.clear_analysis()

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar sannolikhetsetiketter och resultattabellen.
        """
        self.probability_1_label = QLabel()
        self.probability_x_label = QLabel()
        self.probability_2_label = QLabel()

        self.probability_over_25_label = QLabel()
        self.probability_under_25_label = QLabel()
        self.probability_btts_label = QLabel()

        self.score_table = self.create_score_table()

    def create_score_table(self):
        """
            Skapar och returnerar tabellen med de mest sannolika slutresultaten.
        """
        table = BaseTableWidget(
            parent=None,
            readonly=True,
            rowselection=False,
            row_count=self.SCORE_ROW_COUNT,
            headers=self.SCORE_HEADERS
        )

        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table.set_no_selection()

        return table

    def create_layout(self):
        """
            Skapar widgetens layout.
        """
        layout = self.create_vertical_layout(parent=self)

        probability_layout = self.create_grid_layout(
            parent=None,
            horizontal_spacing=self.GRID_HORIZONTAL_SPACING,
            vertical_spacing=self.GRID_VERTICAL_SPACING
        )

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
            self.GRID_COLUMN_COUNT,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        for column in range(self.GRID_COLUMN_COUNT):
            probability_layout.setColumnStretch(
                column,
                1
            )

        layout.addLayout(probability_layout)
        layout.addWidget(self.score_table)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar sannolikheterna från en genomförd matchanalys.
        """
        self.probability_1_label.setText(f"1: {analysis.probability_1:.1%}")
        self.probability_x_label.setText(f"X: {analysis.probability_x:.1%}")
        self.probability_2_label.setText(f"2: {analysis.probability_2:.1%}")

        self.probability_over_25_label.setText(
            f"Över 2.5: {analysis.probability_over_25:.1%}")

        self.probability_under_25_label.setText(
            f"Under 2.5: {analysis.probability_under_25:.1%}"
        )

        self.probability_btts_label.setText(
            f"Båda lagen gör mål: {analysis.probability_btts:.1%}"
        )

        self.fill_score_table(analysis.most_likely_scores)

    # --------------------------------------------------
    # Tabelluppdatering
    # --------------------------------------------------

    def fill_score_table(
        self,
        scores
    ):
        """
            Fyller resultattabellen med de mest sannolika exakta matchresultaten.
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
                QTableWidgetItem(f"{home_goals}–{away_goals}")
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
    # Tillstånd
    # --------------------------------------------------

    def clear_analysis(self):
        """
            Tömmer tidigare sannolikhetsresultat och återställer widgeten.
        """
        self.probability_1_label.setText("1: –")
        self.probability_x_label.setText("X: –")
        self.probability_2_label.setText("2: –")

        self.probability_over_25_label.setText("Över 2.5: –")
        self.probability_under_25_label.setText("Under 2.5: –")
        self.probability_btts_label.setText("Båda lagen gör mål: –")
        self.score_table.clearContents()
        self.score_table.setRowCount(self.SCORE_ROW_COUNT)
