from mvc import Controller
from views.coupon_analysis_view import CouponAnalysisView
from views.match_analysis_view import MatchAnalysisView
from models.competition_model import CompetitionModel
from models.analysis_model import AnalysisModel


class AnalysisController(Controller):
    def __init__(
        self,
        analysis_model,
        competition_model,
        match_view,
        coupon_view
    ):
        super().__init__(analysis_model, match_view)
        self.competition_model = competition_model
        self.analysis_model = analysis_model
        self.coupon_view = coupon_view

        # Ligor, säsonger, matcher och lag
        self.competitions = []
        self.seasons = []
        self.teams = []

        self.current_competition = None
        self.current_season = None
        self.home_team = None
        self.away_team = None

        self.add_connections()
        self.load_competitions()

    def add_connections(self):
        self.view.competition_combo.currentIndexChanged.connect(
            self.competition_changed)
        self.view.season_combo.currentIndexChanged.connect(self.season_changed)
        self.view.home_team_combo.currentIndexChanged.connect(
            self.home_team_changed)
        self.view.away_team_combo.currentIndexChanged.connect(
            self.away_team_changed)
        self.view.analyze_button.clicked.connect(self.analyze_match)

    # Funktion som laddar alla ligor, som finns i databasen.
    def load_competitions(self):
        self.competitions = self.competition_model.get_all()
        self.model.sort_by_keys(self.competitions, "name")
        self.view.fill_competition_combo(self.competitions)

    # Funktion som laddar alla lag för aktuell säsong.
    def load_teams(self):
        if self.current_season is None:
            self.teams = []
            return

        self.teams = self.competition_model.get_teams(self.current_season.id)

    # Funktion som triggas, när vald tävling/liga förändras.
    def competition_changed(self):
        # Aktiv tävling/liga.
        row = self.view.competition_combo.currentIndex()
        # Combo-boxarna inleds med en tom rad.
        if row <= 0 or row > len(self.competitions):
            self.current_competition = None
            self.view.fill_season_combo([])
            return

        self.current_competition = self.competitions[row - 1]
        self.seasons = self.competition_model.get_seasons(
            self.current_competition.id)
        self.view.fill_season_combo(self.seasons)

    def season_changed(self):
        row = self.view.season_combo.currentIndex()

        if row < 0 or row >= len(self.seasons):
            self.current_season = None
            self.teams = []
            self.view.fill_team_combos([])

            return

        self.current_season = self.seasons[row]
        self.teams = self.competition_model.get_teams(
            self.current_season.id
        )

        self.home_team = None
        self.away_team = None

        self.view.fill_home_team_combo(self.teams)
        self.view.fill_away_team_combo(self.teams)

    def home_team_changed(self):
        self.home_team = (
            self.view.home_team_combo.currentData()
        )

        self.update_away_team_combo()

    def away_team_changed(self):
        self.away_team = (
            self.view.away_team_combo.currentData()
        )

    def get_available_away_teams(self):
        if self.home_team is None:
            return self.teams

        return [
            team
            for team in self.teams
            if team.id != self.home_team.id
        ]

    def update_away_team_combo(self):
        teams = self.get_available_away_teams()

        self.away_team = None
        self.view.away_team_combo.blockSignals(True)
        self.view.fill_away_team_combo(teams)
        self.view.away_team_combo.blockSignals(False)

    def analyze_match(self):
        pass
