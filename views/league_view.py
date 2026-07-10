from mvc import View
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton,
    QStackedWidget,
    QGridLayout,
    QLineEdit,
    QSpinBox,
    QFrame,
    QFileDialog
)
from misc.base_table_widget import BaseTableWidget

# Klass (View) som visar information om lag, tabeller med mera.


class LeagueView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Ligor")
        self.layout.addWidget(self.header)

        # Innehållsväxling
        self.stacked_widget = QStackedWidget()

        # Skapa de widgetar som ska ingå i QStackedWidget.
        self.create_overview_widget()
        self.create_details_widget()

        # Lägg till i QStackedWidget.
        self.stacked_widget.addWidget(self.overview_widget)
        self.stacked_widget.addWidget(self.details_widget)
        self.layout.addWidget(self.stacked_widget)

        # Knappar
        self.create_bottom_widget()

        self.setLayout(self.layout)
        self.show_overview()

    # Funktion som skapar tabellen med ligor.
    def create_overview_widget(self):
        self.overview_widget = QWidget()
        layout = QVBoxLayout()

        self.league_table = BaseTableWidget(True, True, 0, 3)

        self.league_table.setHorizontalHeaderLabels([
            "Id",
            "Land",
            "Namn"
        ])

        layout.addWidget(self.league_table)

        self.overview_widget.setLayout(layout)

    def create_details_widget(self):

        self.details_widget = QWidget()
        layout = QVBoxLayout()

        # Information om ligan.
        self.league_name_label = QLabel()
        self.country_label = QLabel()

        layout.addWidget(self.league_name_label)
        layout.addWidget(self.country_label)

        # Säsonger.
        layout.addWidget(QLabel("Säsonger"))

        self.season_table = BaseTableWidget(True, True, 0, 2)
        self.season_table.setHorizontalHeaderLabels([
            "Id",
            "Säsong"
        ])

        self.season_table.set_narrow_column(0)
        self.season_table.set_wide_column(1)

        layout.addWidget(self.season_table)

        # Lag.
        layout.addWidget(QLabel("Lag"))

        self.team_table = BaseTableWidget(True, True, 0, 2)
        self.team_table.setHorizontalHeaderLabels([
            "Id",
            "Lag"
        ])

        self.team_table.set_narrow_column(0)
        self.team_table.set_wide_column(1)

        layout.addWidget(self.team_table)

        self.details_widget.setLayout(layout)

    # Funktion som skapar den undre widgeten med olika knappar.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.back_to_overview_button = QPushButton("Tillbaka")
        layout.addWidget(self.back_to_overview_button)

        self.add_league_button = QPushButton("Lägg till")
        layout.addWidget(self.add_league_button)

        self.show_info_button = QPushButton("Visa information")
        layout.addWidget(self.show_info_button)

        self.delete_league_button = QPushButton("Radera")
        self.delete_league_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_league_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

        self.show_overview()

    # Funktion som körs, när tabellen med ligor uppdateras.
    def update_league_table(self, leagues):

        self.league_table.clearContents()
        self.league_table.setRowCount(len(leagues))

        for row, league in enumerate(leagues):

            self.league_table.setItem(
                row, 0, QTableWidgetItem(str(league.id))
            )

            self.league_table.setItem(
                row, 1, QTableWidgetItem(league.name)
            )

            self.league_table.setItem(
                row, 2, QTableWidgetItem(league.country)
            )

        self.league_table.set_narrow_columns([0, 1])
        self.league_table.set_wide_column(2)

    # Funktion som körs, när tabellen med säsonger uppdateras.
    def update_season_table(self, seasons):

        self.season_table.clearContents()
        self.season_table.setRowCount(len(seasons))

        for row, season in enumerate(seasons):

            self.season_table.setItem(
                row,
                0,
                QTableWidgetItem(str(season.id))
            )

            self.season_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{season.start_year}/{season.end_year}"
                )
            )

        # Inställning av bredd för olika kolumner.
        self.season_table.set_narrow_column(0)
        self.season_table.set_wide_column(1)

    # Funktion som körs, när tabellen med lagen i säsongerna uppdateras.
    def update_team_table(self, teams):

        self.team_table.clearContents()
        self.team_table.setRowCount(len(teams))

        for row, team in enumerate(teams):

            self.team_table.setItem(
                row,
                0,
                QTableWidgetItem(str(team.id))
            )

            self.team_table.setItem(
                row,
                1,
                QTableWidgetItem(team.name)
            )

        self.team_table.set_narrow_column(0)
        self.team_table.set_wide_column(1)

    # Uppdatera informationen om ligan.
    def update_league_info(self, league):

        self.league_name_label.setText(
            f"Namn: {league.name}"
        )

        self.country_label.setText(
            f"Land: {league.country}"
        )

    # Funktion för att visa översikten.
    def show_overview(self):
        self.back_to_overview_button.hide()
        self.add_league_button.show()
        self.show_info_button.show()
        self.delete_league_button.show()
        self.clear()
        self.stacked_widget.setCurrentWidget(self.overview_widget)

    # Funktion för att visa vyn med tabellerna med information om säsonger och lag för en viss liga.
    def show_details(self):
        self.back_to_overview_button.show()
        self.add_league_button.hide()
        self.show_info_button.hide()
        self.delete_league_button.hide()
        self.stacked_widget.setCurrentWidget(self.details_widget)

    def clear(self):
        self.league_table.clearSelection()

    def get_active_selection_table(self):
        return self.league_table
