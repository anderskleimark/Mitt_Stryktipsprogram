from misc.country import Country
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
from PySide6.QtCore import Qt
from misc.base_table_widget import BaseTableWidget

# Klass (View) som visar information om tävlingar/lag, tabeller med mera.


class CompetitionView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Tävlingar och ligor")
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

        self.competition_table = BaseTableWidget(True, True, 0, 3)

        self.competition_table.setHorizontalHeaderLabels([
            "Id",
            "Land",
            "Namn"
        ])

        layout.addWidget(self.competition_table)

        self.overview_widget.setLayout(layout)

    def create_details_widget(self):

        self.details_widget = QWidget()
        layout = QVBoxLayout()

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

        season_buttons = QHBoxLayout()

        # Knappar för att lägga till och radera en säsong.
        self.add_season_button = QPushButton("Lägg till säsong")
        season_buttons.addWidget(self.add_season_button)

        self.delete_season_button = QPushButton("Radera säsong")
        season_buttons.addWidget(self.delete_season_button)

        season_buttons.addStretch()
        layout.addLayout(season_buttons)

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

        team_buttons = QHBoxLayout()

        # Knappar för att kunna lägga till och radera lag.
        self.add_team_button = QPushButton("Lägg till lag")
        team_buttons.addWidget(self.add_team_button)

        self.delete_team_button = QPushButton("Radera lag")
        team_buttons.addWidget(self.delete_team_button)

        team_buttons.addStretch()

        layout.addLayout(team_buttons)

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

        self.add_competition_button = QPushButton("Lägg till")
        layout.addWidget(self.add_competition_button)

        self.show_info_button = QPushButton("Visa information")
        layout.addWidget(self.show_info_button)

        self.delete_competition_button = QPushButton("Radera")
        self.delete_competition_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_competition_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

        self.show_overview()

    # Funktion som körs, när tabellen med tävlingar/ligor uppdateras.
    def update_competition_table(self, competitions):

        self.competition_table.clearContents()
        self.competition_table.setRowCount(len(competitions))

        for row, competition in enumerate(competitions):

            self.competition_table.setItem(
                row,
                0,
                QTableWidgetItem(str(competition.id))
            )

            country_item = QTableWidgetItem(
                f"{Country.get_flag(competition.country)} "
                f"{competition.country}"
            )

            self.competition_table.setItem(
                row,
                1,
                country_item
            )

            self.competition_table.setItem(
                row,
                2,
                QTableWidgetItem(competition.name)
            )

        self.competition_table.set_narrow_columns([0, 1])
        self.competition_table.set_wide_column(2)

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

    # Funktion för att uppdatera informationen om tävlingen/ligan.
    def update_competition_info(self, competition):

        self.update_header_text(
            f"{Country.get_flag(competition.country)} "
            f"{competition.name}"
        )

    # Funktion för att visa översikten.
    def show_overview(self):
        self.update_header_text("Tävlingar och ligor")
        self.back_to_overview_button.hide()
        self.add_competition_button.show()
        self.show_info_button.show()
        self.delete_competition_button.show()
        self.clear()
        self.stacked_widget.setCurrentWidget(self.overview_widget)

    # Funktion för att visa vyn med tabellerna med information om säsonger och lag för en viss liga.
    def show_details(self):
        self.back_to_overview_button.show()
        self.add_competition_button.hide()
        self.show_info_button.hide()
        self.delete_competition_button.hide()
        self.stacked_widget.setCurrentWidget(self.details_widget)

    # Funktion för att rensa och återställa.
    def clear(self):
        self.competition_table.clearSelection()
        self.season_table.clearSelection()
        self.team_table.clearSelection()

    # Superfunktion som ser till att alla markeringar försvinner, om användaren klickar utanför tabellerna.
    def get_active_selection_table(self):

        if self.stacked_widget.currentWidget() == self.overview_widget:
            return self.competition_table

        if self.stacked_widget.currentWidget() == self.details_widget:

            # Om en säsong är markerad
            if self.season_table.selectedItems():
                return self.season_table

            # Om ett lag är markerat
            if self.team_table.selectedItems():
                return self.team_table

        return None
