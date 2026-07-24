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
        super().__init__(match_view)
        self.analysis_model = analysis_model
        self.competition_model = competition_model
        self.analysis_model = analysis_model
        self.coupon_view = coupon_view

        # Ligor, säsonger, matcher och lag
        self.competitions = []
        self.seasons = []
        self.teams = []

        self.competition = None
        self.season = None
        self.home_team = None
        self.away_team = None

        self.add_connections()
        self.load_competitions()
        self.update_analyze_button_status()

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
        self.analysis_model.sort_by_keys(self.competitions, "name")
        self.view.fill_competition_combo(self.competitions)

    # Funktion som laddar alla lag för aktuell säsong.
    def load_teams(self):
        if self.season is None:
            self.teams = []
            self.home_team = None
            self.away_team = None
            return

        self.teams = self.competition_model.get_teams(self.season.id)
        self.analysis_model.sort_by_keys(self.competitions, "name")

    # Funktion som triggas, när vald tävling/liga förändras.
    def competition_changed(self):
        # Aktiv tävling/liga.
        row = self.view.competition_combo.currentIndex()
        # Combo-boxarna inleds med en tom rad.
        if row <= 0 or row > len(self.competitions):
            self.competition = None
            self.view.fill_season_combo([])
            return

        self.competition = self.competitions[row - 1]
        self.seasons = self.competition_model.get_seasons(
            self.competition.id)
        self.view.fill_season_combo(self.seasons)
        self.update_analyze_button_status()

    # Funktion som triggas, när vald säsong förändras.
    def season_changed(self):
        row = self.view.season_combo.currentIndex()

        if row < 0 or row >= len(self.seasons):
            self.season = None
            self.teams = []
            self.view.fill_team_combos([])

            return

        self.season = self.seasons[row]
        self.teams = self.competition_model.get_teams(
            self.season.id
        )

        # När säsongen byts sätts hemmalaget och bortalaget till None.
        self.home_team = None
        self.away_team = None

        self.view.fill_home_team_combo(self.teams)
        self.view.fill_away_team_combo(self.teams)
        self.update_analyze_button_status()

    # Funktion som triggas, när valt hemmalag ändras.
    def home_team_changed(self):
        self.home_team = (
            self.view.home_team_combo.currentData()
        )

        self.update_away_team_combo()
        self.update_analyze_button_status()

    # Funktion som triggas, när valt bortalag ändras.
    def away_team_changed(self):
        self.away_team = (
            self.view.away_team_combo.currentData()
        )
        self.update_analyze_button_status()

    # Funktion som returnerar tillgängliga bortalag.
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
        analysis = self.analysis_model.analyze_match(
            self.season,
            self.home_team,
            self.away_team
        )

        self.view.show_analysis(analysis)

    def update_analyze_button_status(self):
        if (
            self.competition is None
            or self.season is None
            or self.home_team is None
            or self.away_team is None
        ):
            self.view.analyze_button.setEnabled(False)
        else:
            self.view.analyze_button.setEnabled(True)
