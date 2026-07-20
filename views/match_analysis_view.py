from mvc import View
from PySide6.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QStackedWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget, QComboBox)
from misc.base_combo_box import BaseComboBox


class MatchAnalysisView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Matchanalys")
        self.layout.addWidget(self.header)

        # Bygg UI
        self.create_match_selection_widget()

        self.setLayout(self.layout)

    def create_match_selection_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()

        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(10)

        # Tävling / liga.
        layout.addWidget(QLabel("Liga"))
        self.competition_combo = BaseComboBox()
        layout.addWidget(self.competition_combo, 2)

        # Säsong.
        layout.addWidget(QLabel("Säsong"))
        self.season_combo = BaseComboBox()
        layout.addWidget(self.season_combo, 1)

        # Hemmalag.
        layout.addWidget(QLabel("Hemmalag"))
        self.home_team_combo = BaseComboBox()
        layout.addWidget(self.home_team_combo, 2)

        # Bortalag.
        layout.addWidget(QLabel("Bortalag"))
        self.away_team_combo = BaseComboBox()
        layout.addWidget(self.away_team_combo, 2)

        # Analysera-knapp.
        self.analyze_button = QPushButton("Analysera")
        layout.addWidget(self.analyze_button)

        # Layout.
        widget.setLayout(layout)
        self.layout.addWidget(widget)

    def fill_competition_combo(self, competitions: list = []):
        self.competition_combo.blockSignals(True)
        self.competition_combo.clear_with_empty_item()

        for competition in competitions:
            self.competition_combo.addItem(competition.name)

        self.competition_combo.blockSignals(False)

    def fill_season_combo(self, seasons: list = []):

        self.season_combo.clear()

        for season in seasons:
            self.season_combo.addItem(season.name)

    def fill_team_combos(self, teams):
        self.home_team_combo.blockSignals(True)
        self.away_team_combo.blockSignals(True)

        self.fill_home_team_combo(teams)
        self.fill_away_team_combo(teams)

        self.home_team_combo.blockSignals(False)
        self.away_team_combo.blockSignals(False)

    def fill_home_team_combo(self, teams):
        self.home_team_combo.blockSignals(True)
        self.home_team_combo.clear_with_empty_item()

        for team in teams:
            self.home_team_combo.addItem(
                team.name,
                team
            )

        self.home_team_combo.blockSignals(False)

    def fill_away_team_combo(self, teams):
        self.away_team_combo.blockSignals(True)
        self.away_team_combo.clear_with_empty_item()

        for team in teams:
            self.away_team_combo.addItem(
                team.name,
                team
            )

        self.away_team_combo.blockSignals(False)
