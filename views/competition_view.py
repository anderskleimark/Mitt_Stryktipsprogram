from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QStackedWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.country import Country
from mvc import View

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
        self.create_standings_widget()

        # Lägg till i QStackedWidget.
        self.stacked_widget.addWidget(self.overview_widget)
        self.stacked_widget.addWidget(self.details_widget)
        self.stacked_widget.addWidget(self.standings_widget)

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
        self.competition_table.setHorizontalHeaderLabels(
            ["Id", "Land", "Namn"])

        layout.addWidget(self.competition_table)
        self.overview_widget.setLayout(layout)

    # Funktion för att skapa detaljvyn.
    def create_details_widget(self):

        self.details_widget = QWidget()
        layout = QVBoxLayout()

        # Säsonger
        layout.addWidget(QLabel("Säsonger"))

        self.season_table = BaseTableWidget(True, True, 0, 2)
        self.season_table.setHorizontalHeaderLabels(["Id", "Säsong"])
        self.season_table.set_narrow_column(0)
        self.season_table.set_wide_column(1)

        layout.addWidget(self.season_table)

        # Knappar för säsonger
        season_buttons = QHBoxLayout()

        self.add_season_button = QPushButton("Lägg till säsong")
        season_buttons.addWidget(self.add_season_button)

        self.delete_season_button = QPushButton("Radera säsong")

        season_buttons.addWidget(self.delete_season_button)
        season_buttons.addStretch()

        layout.addLayout(season_buttons)

        # Lag
        layout.addWidget(QLabel("Lag"))

        self.team_table = BaseTableWidget(True, True, 0, 2)
        self.team_table.setHorizontalHeaderLabels(["Id", "Lag"])
        self.team_table.set_narrow_column(0)
        self.team_table.set_wide_column(1)

        layout.addWidget(self.team_table)

        # Knappar för lag
        team_buttons = QHBoxLayout()

        self.add_team_button = QPushButton("Lägg till lag")

        team_buttons.addWidget(self.add_team_button)
        self.delete_team_button = QPushButton("Radera lag")

        team_buttons.addWidget(self.delete_team_button)
        team_buttons.addStretch()

        layout.addLayout(team_buttons)
        self.details_widget.setLayout(layout)

    def create_team_widget(self):
        self.team_widget = QWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Lag"))

        self.team_table = BaseTableWidget(True, True, 0, 2)
        self.team_table.setHorizontalHeaderLabels(["Id", "Lag"])

        self.team_table.set_narrow_column(0)
        self.team_table.set_wide_column(1)

        layout.addWidget(self.team_table)
        team_buttons = QHBoxLayout()

        self.add_team_button = QPushButton("Lägg till lag")
        team_buttons.addWidget(self.add_team_button)

        self.delete_team_button = QPushButton("Radera lag")
        team_buttons.addWidget(self.delete_team_button)

        team_buttons.addStretch()
        layout.addLayout(team_buttons)

        self.team_widget.setLayout(layout)

    # Funktion för att skapa en kontrollpanel med knappar för att lägga till, redigera
    # och radera matcher för valt lag.
    def create_matches_controlpanel_widget(self):
        self.matches_controlpanel_widget = QWidget()
        layout = QHBoxLayout()

        # Knappar
        self.add_match_button = QPushButton("Lägg till match")
        layout.addWidget(self.add_match_button)

        self.edit_match_button = QPushButton("Redigera match")
        layout.addWidget(self.edit_match_button)

        self.delete_match_button = QPushButton("Radera match")
        layout.addWidget(self.delete_match_button)

        layout.addStretch()

        # Layout.
        self.matches_controlpanel_widget.setLayout(layout)

    def create_standings_widget(self):
        self.standings_widget = QWidget()

        # Huvudlayout.

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 15, 0, 0)
        main_layout.setSpacing(30)

        # Vänster panel.

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("Serie-tabell"))

        self.standings_table = BaseTableWidget(True, True, 0, 7)

        self.standings_table.setHorizontalHeaderLabels(
            ["Lag", "Sp", "V", "O", "F", "Mål", "Poäng"])

        self.standings_table.set_wide_column(0)
        self.standings_table.set_narrow_columns([1, 2, 3, 4, 5, 6])

        left_layout.addWidget(self.standings_table, stretch=1)

        # Höger panel.

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Rubrik

        self.team_info_label = QLabel()
        right_layout.addWidget(self.team_info_label)
        right_layout.addSpacing(8)

        # Statistik

        statistics_label = QLabel("Statistik")
        statistics_label.setStyleSheet("font-weight: bold;")

        right_layout.addWidget(statistics_label)

        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)

        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setHorizontalSpacing(10)
        stats_layout.setVerticalSpacing(4)

        stats_layout.addWidget(QLabel("Matcher:"), 0, 0)
        self.played_label = QLabel("-")
        stats_layout.addWidget(self.played_label, 0, 1)

        stats_layout.addWidget(QLabel("Mål:"), 1, 0)
        self.goals_label = QLabel("-")
        stats_layout.addWidget(self.goals_label, 1, 1)

        stats_layout.addWidget(QLabel("Målskillnad:"), 2, 0)
        self.goal_difference_label = QLabel("-")
        stats_layout.addWidget(self.goal_difference_label, 2, 1)

        stats_layout.addWidget(QLabel("Poäng:"), 3, 0)
        self.points_label = QLabel("-")
        stats_layout.addWidget(self.points_label, 3, 1)

        right_layout.addWidget(stats_widget)

        # Luft.

        right_layout.addSpacing(10)

        # Matcher

        matches_label = QLabel("Matcher")
        matches_label.setStyleSheet("font-weight: bold;")

        right_layout.addWidget(matches_label)

        self.team_matches_table = BaseTableWidget(True, True, 0, 4)

        self.team_matches_table.setHorizontalHeaderLabels([
            "Datum",
            "Hemmalag",
            "Bortalag",
            "Resultat"
        ])
        self.team_matches_table.set_narrow_columns([0, 3])
        self.team_matches_table.set_wide_columns([1, 2])

        right_layout.addWidget(self.team_matches_table, stretch=1)
        self.create_matches_controlpanel_widget()
        right_layout.addWidget(self.matches_controlpanel_widget)

        # Lägg panelerna bredvid varandra.

        main_layout.addWidget(left_widget, stretch=3)
        main_layout.addWidget(right_widget, stretch=2)

        # Layout.
        self.standings_widget.setLayout(main_layout)

    # Funktion som skapar den undre widgeten med olika knappar.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.back_to_overview_button = QPushButton("Tillbaka")
        layout.addWidget(self.back_to_overview_button)

        self.back_to_details_button = QPushButton("Tillbaka")
        layout.addWidget(self.back_to_details_button)

        self.show_standing_table_button = QPushButton("Visa tabell")
        layout.addWidget(self.show_standing_table_button)

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
                row, 0, QTableWidgetItem(str(competition.id)))

            country_item = QTableWidgetItem(
                f"{Country.get_flag(competition.country)} "f"{competition.country}")

            self.competition_table.setItem(row, 1, country_item)
            self.competition_table.setItem(
                row, 2, QTableWidgetItem(competition.name))

        self.competition_table.set_narrow_columns([0, 1])
        self.competition_table.set_wide_column(2)

    # Funktion som körs, när tabellen med säsonger uppdateras.
    def update_season_table(self, seasons):

        self.season_table.clearContents()
        self.season_table.setRowCount(len(seasons))

        for row, season in enumerate(seasons):
            self.season_table.setItem(row, 0, QTableWidgetItem(str(season.id)))
            self.season_table.setItem(row, 1, QTableWidgetItem(
                f"{season.start_year}/{season.end_year}"))

        # Inställning av bredd för olika kolumner.
        self.season_table.set_narrow_column(0)
        self.season_table.set_wide_column(1)

    # Funktion som körs, när tabellen med lagen i säsongerna uppdateras.
    def update_team_table(self, teams):

        self.team_table.clearContents()
        self.team_table.setRowCount(len(teams))

        for row, team in enumerate(teams):
            self.team_table.setItem(row, 0, QTableWidgetItem(str(team.id)))
            self.team_table.setItem(row, 1, QTableWidgetItem(team.name))

        self.team_table.set_narrow_column(0)
        self.team_table.set_wide_column(1)

    # Funktion för att uppdatera informationen om tävlingen/ligan.
    def update_competition_info(self, competition):
        self.update_header_text(
            f"{Country.get_flag(competition.country)} "
            f"{competition.name}"
        )

    # Funktion för att uppdatera serie-tabellen.
    def update_standings_table(self, standings):

        self.standings_table.clearContents()
        self.standings_table.setRowCount(len(standings))

        for row, standing in enumerate(standings):

            # Lag
            self.standings_table.setItem(
                row, 0, QTableWidgetItem(standing.name))

            # Spelade
            self.standings_table.setItem(
                row, 1, QTableWidgetItem(str(standing.played)))

            # Vunna
            self.standings_table.setItem(
                row, 2, QTableWidgetItem(str(standing.wins)))

            # Oavgjorda
            self.standings_table.setItem(
                row, 3, QTableWidgetItem(str(standing.draws)))

            # Förlorade
            self.standings_table.setItem(
                row, 4, QTableWidgetItem(str(standing.losses)))

            # Mål
            self.standings_table.setItem(row, 5, QTableWidgetItem(
                f"{standing.goals_for} – "f"{standing.goals_against}"))

            # Poäng
            self.standings_table.setItem(
                row, 6, QTableWidgetItem(str(standing.points)))

        # Anpassa kolumnbredder
        self.standings_table.set_wide_column(0)
        self.standings_table.set_narrow_columns([1, 2, 3, 4, 5, 6])

    # Funktion för att uppdatera statistiken för det valda laget.
    def update_team_statistics(self, standing):

        self.team_info_label.setText(standing.name)
        self.played_label.setText(str(standing.played))
        self.goals_label.setText(
            f"{standing.goals_for} – {standing.goals_against}")

        goal_difference = (standing.goals_for - standing.goals_against)

        self.goal_difference_label.setText(f"{goal_difference:+d}")
        self.points_label.setText(str(standing.points))

    # Funktion för att uppdatera information om lagets spelade matcher under säsongen.
    def update_team_matches(self, matches):

        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(len(matches))

        for row, match in enumerate(matches):
            self.team_matches_table.setItem(row, 0,
                                            QTableWidgetItem(str(match.match_date)))

            self.team_matches_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    match.home_team.name
                )
            )

            self.team_matches_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    match.away_team.name
                )
            )

            result = ""

            if match.home_score is not None and match.away_score is not None:
                result = f"{match.home_score} – {match.away_score}"

            self.team_matches_table.setItem(row, 3, QTableWidgetItem(result))

        self.team_matches_table.set_narrow_columns([0, 3])
        self.team_matches_table.set_wide_columns([1, 2])

    # Funktion för att visa översikten.
    def show_overview(self):
        self.update_header_text("Tävlingar och ligor")
        self.back_to_overview_button.hide()
        self.add_competition_button.show()
        self.show_info_button.show()
        self.delete_competition_button.show()
        self.show_standing_table_button.hide()
        self.back_to_details_button.hide()
        self.clear()
        self.stacked_widget.setCurrentWidget(self.overview_widget)

    # Funktion för att visa vyn med tabellerna med information om säsonger
    # och lag för en viss liga.
    def show_details(self):
        self.back_to_overview_button.show()
        self.show_standing_table_button.show()
        self.add_competition_button.hide()
        self.show_info_button.hide()
        self.delete_competition_button.hide()
        self.back_to_details_button.hide()
        self.stacked_widget.setCurrentWidget(self.details_widget)

    # Funktion för att visa serie-tabellen för vald säsong.
    def show_standings(self):
        self.back_to_overview_button.hide()
        self.show_standing_table_button.hide()
        self.back_to_details_button.show()
        self.add_match_button.setEnabled(False)
        self.edit_match_button.setEnabled(False)
        self.delete_match_button.setEnabled(False)
        self.stacked_widget.setCurrentWidget(self.standings_widget)

    def clear_selection(self):
        table = self.view.get_active_selection_table()

        if table:
            table.clearSelection()

            if table == self.view.standings_table:
                self.view.clear_team_information()

    # Funktion för att rensa och återställa.
    def clear(self):
        self.competition_table.clearSelection()
        self.season_table.clearSelection()
        self.team_table.clearSelection()

        if hasattr(self, "standings_table"):
            self.standings_table.clearSelection()

        if hasattr(self, "team_matches_table"):
            self.team_matches_table.clearSelection()

    # Funktion som rensar informationen om valt lag.
    def clear_team_information(self):

        self.team_info_label.setText(
            "Laginformation"
        )

        self.played_label.setText("-")
        self.goals_label.setText("-")
        self.goal_difference_label.setText("-")
        self.points_label.setText("-")

        self.team_matches_table.clearContents()
        self.team_matches_table.setRowCount(0)

    # Superfunktion som ser till att alla markeringar försvinner,
    # om användaren klickar utanför tabellerna.
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

        if self.stacked_widget.currentWidget() == self.standings_widget:

            # Om ett lag i serietabellen är markerat
            if self.standings_table.selectedItems():
                return self.standings_table

            # Om en match i matchtabellen är markerad
            if self.team_matches_table.selectedItems():
                return self.team_matches_table

        return None
