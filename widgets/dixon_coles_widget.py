from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QLabel, QTableWidgetItem

from misc.base_table_widget import BaseTableWidget
from widgets.base_widget import BaseWidget


class DixonColesWidget(BaseWidget):
    """
        Widget för att visa resultat från
        Dixon-Coles-modellen.

        Widgeten visar förväntat antal mål för
        hemma- och bortalaget, modellens rho-värde
        samt lagens Poissonfördelningar.
    """

    # --------------------------------------------------
    # Tabeller
    # --------------------------------------------------

    POISSON_ROW_COUNT = 6

    # --------------------------------------------------
    # Tabellrubriker
    # --------------------------------------------------

    POISSON_HEADERS = (
        "Mål",
        "Sannolikhet"
    )

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    LABEL_HOME_TEAM = "Hemmalag"
    LABEL_AWAY_TEAM = "Bortalag"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    GRID_HORIZONTAL_SPACING = 20
    GRID_VERTICAL_SPACING = 10

    def __init__(self):
        """
            Initierar Dixon-Coles-widgeten.
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
            Skapar etiketter och Poisson-tabeller.
        """
        self.rho_label = QLabel()
        self.rho_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.home_team_label = QLabel(self.LABEL_HOME_TEAM)
        self.home_team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.away_team_label = QLabel(self.LABEL_AWAY_TEAM)
        self.away_team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.home_lambda_label = QLabel()
        self.home_lambda_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.away_lambda_label = QLabel()

        self.away_lambda_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.home_poisson_table = self.create_poisson_table()
        self.away_poisson_table = self.create_poisson_table()

    def create_poisson_table(self):
        """
            Skapar och returnerar en tabell för en Poissonfördelning.
        """
        table = BaseTableWidget(
            readonly=True,
            selection="item",
            row_count=self.POISSON_ROW_COUNT,
            headers=self.POISSON_HEADERS
        )

        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table.set_no_selection()

        return table

    def create_layout(self):
        """
            Skapar widgetens huvudlayout och layouten för Poissonfördelningarna.
        """
        layout = self.create_vertical_layout(parent=self)

        layout.addWidget(self.rho_label)

        distributions_layout = self.create_grid_layout(
            horizontal_spacing=self.GRID_HORIZONTAL_SPACING,
            vertical_spacing=self.GRID_VERTICAL_SPACING
        )

        distributions_layout.addWidget(
            self.home_team_label,
            0,
            0
        )

        distributions_layout.addWidget(
            self.away_team_label,
            0,
            1
        )

        distributions_layout.addWidget(
            self.home_lambda_label,
            1,
            0
        )

        distributions_layout.addWidget(
            self.away_lambda_label,
            1,
            1
        )

        distributions_layout.addWidget(
            self.home_poisson_table,
            2,
            0
        )

        distributions_layout.addWidget(
            self.away_poisson_table,
            2,
            1
        )

        distributions_layout.setColumnStretch(
            0,
            1
        )

        distributions_layout.setColumnStretch(
            1,
            1
        )

        layout.addLayout(distributions_layout)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar Dixon-Coles-resultatet från en genomförd matchanalys.
        """
        self.rho_label.setText(f"ρ = {analysis.rho:.3f}")

        self.home_lambda_label.setText(
            f"λ = {analysis.lambda_home:.2f}"
        )

        self.away_lambda_label.setText(f"λ = {analysis.lambda_away:.2f}")

        self.fill_poisson_table(
            self.home_poisson_table,
            analysis.home_poisson
        )

        self.fill_poisson_table(
            self.away_poisson_table,
            analysis.away_poisson
        )

    # --------------------------------------------------
    # Tabelluppdatering
    # --------------------------------------------------

    def fill_poisson_table(
        self,
        table,
        distribution
    ):
        """
            Fyller en Poisson-tabell med målantal och motsvarande sannolikheter.
        """
        table.clearContents()

        if not distribution:
            return

        table.setRowCount(len(distribution))

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

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_analysis(self):
        """
            Tömmer tidigare Dixon-Coles-resultat och återställer widgeten.
        """
        self.rho_label.setText("ρ = –")

        self.home_lambda_label.setText("λ = –")
        self.away_lambda_label.setText("λ = –")

        self.home_poisson_table.clearContents()
        self.away_poisson_table.clearContents()

        self.home_poisson_table.setRowCount(self.POISSON_ROW_COUNT)
        self.away_poisson_table.setRowCount(self.POISSON_ROW_COUNT)
