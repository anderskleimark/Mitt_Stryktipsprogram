from mvc import Controller


class AnalysisController(Controller):
    """
        Controller som hanterar analys av fotbollsmatcher.
    """

    NO_ROW_SELECTED = -1

    def __init__(
        self,
        *,
        analysis_model,
        competition_model,
        soccer_model,
        match_view,
        coupon_view
    ):
        """
            Initierar controllern.
        """
        super().__init__(match_view)

        self.analysis_model = analysis_model
        self.competition_model = competition_model
        self.soccer_model = soccer_model
        self.coupon_view = coupon_view

        # Ligor, säsonger, matcher och lag
        self.competitions = []
        self.seasons = []
        self.teams = []

        self.selected_competition = None
        self.selected_season = None
        self.selected_home_team = None
        self.selected_away_team = None

        self.add_connections()
        self.load_competitions()
        self.view.enter_pre_analyze_state()

    def add_connections(self):
        """
            Kopplar signaler från vyn till controllern.
        """
        self.view.competition_combo.currentIndexChanged.connect(
            self.on_selected_competition_changed
        )

        self.view.season_combo.currentIndexChanged.connect(
            self.on_selected_season_changed
        )

        self.view.home_team_combo.currentIndexChanged.connect(
            self.on_selected_home_team_changed
        )

        self.view.away_team_combo.currentIndexChanged.connect(
            self.on_selected_away_team_changed
        )

        self.view.analyze_button.clicked.connect(
            self.on_analyze_match_clicked
        )

        self.view.statistics_button.clicked.connect(
            self.on_statistics_button_clicked
        )

        self.view.poisson_button.clicked.connect(
            self.on_poisson_button_clicked
        )

        self.view.probability_button.clicked.connect(
            self.on_probability_button_clicked
        )

        self.view.odds_button.clicked.connect(
            self.on_odds_button_clicked
        )

        self.view.clear_button.clicked.connect(
            self.on_clear_analysis_clicked
        )

    def load_competitions(self):
        """
            Hämtar och visar tillgängliga tävlingar.
        """
        self.competitions = (
            self.competition_model.get_all()
        )

        self.view.fill_competition_combo(
            self.competitions
        )

    def on_selected_competition_changed(self):
        """
            Hanterar byte av vald tävling.
        """
        row = self.view.competition_combo.currentIndex()

        # Återställ underordnade val.
        self.selected_season = None
        self.selected_home_team = None
        self.selected_away_team = None

        self.seasons = []
        self.teams = []

        self.view.fill_season_combo([])
        self.view.fill_team_combos([])

        if row < 0 or row >= len(self.competitions):
            self.selected_competition = None
            self.update_buttons()
            return

        self.selected_competition = self.competitions[row]

        self.seasons = self.soccer_model.get_seasons(
            self.selected_competition.id)

        self.view.fill_season_combo(self.seasons)
        self.update_buttons()

    def on_selected_season_changed(self):
        """
            Hanterar byte av vald säsong.
        """
        row = self.view.season_combo.currentIndex()

        # Återställ lagvalen.
        self.selected_home_team = None
        self.selected_away_team = None

        self.teams = []

        self.view.fill_team_combos([])

        if row < 0 or row >= len(self.seasons):
            self.selected_season = None
            self.update_buttons()
            return

        self.selected_season = self.seasons[row]

        self.teams = (
            self.soccer_model.get_teams_in_season(self.selected_season.id)
        )
        self.view.fill_home_team_combo(self.teams)
        self.view.fill_away_team_combo(self.teams)
        self.update_buttons()

    def on_selected_home_team_changed(self):
        """
            Hanterar byte av hemmalag.
        """
        self.selected_home_team = (
            self.view.home_team_combo.currentData()
        )

        self.update_away_team_combo()
        self.update_buttons()

    def on_selected_away_team_changed(self):
        """
            Hanterar byte av bortalag.
        """
        self.selected_away_team = (
            self.view.away_team_combo.currentData()
        )

        self.update_buttons()

    def get_available_away_teams(self):
        """
            Returnerar tillgängliga bortalag.
        """
        if self.selected_home_team is None:
            return self.teams

        return [
            team
            for team in self.teams
            if team.id != self.selected_home_team.id
        ]

    def update_away_team_combo(self):
        """
            Uppdaterar listan med tillgängliga bortalag.
        """
        teams = self.get_available_away_teams()

        self.selected_away_team = None
        self.view.away_team_combo.blockSignals(True)

        self.view.fill_away_team_combo(teams)
        self.view.away_team_combo.blockSignals(False)

    def on_analyze_match_clicked(self):
        """
            Genomför analys av vald match.
        """
        analysis = self.analysis_model.analyze_match(
            self.selected_season,
            self.selected_home_team,
            self.selected_away_team
        )

        self.view.show_analysis(analysis)
        self.update_buttons()
        self.view.enter_view_state()

    def on_statistics_button_clicked(self):
        """
            Visar statistikvyn.
        """
        self.view.show_statistics()

    def on_poisson_button_clicked(self):
        """
            Visar Poisson-vyn.
        """
        self.view.show_poisson()

    def on_probability_button_clicked(self):
        """
            Visar sannolikhetsvyn.
        """
        self.view.show_probabilities()

    def on_odds_button_clicked(self):
        """
            Visar oddsvyn.
        """
        self.view.show_odds()

    def update_buttons(self):
        """
            Uppdaterar analys- och rensningsknapparna.
        """
        ready = (
            self.selected_competition is not None
            and self.selected_season is not None
            and self.selected_home_team is not None
            and self.selected_away_team is not None
        )

        has_selection = (
            self.selected_competition is not None
            or self.selected_season is not None
            or self.selected_home_team is not None
            or self.selected_away_team is not None
        )

        self.view.analyze_button.setEnabled(ready)
        self.view.clear_button.setEnabled(has_selection)

    def on_clear_analysis_clicked(self):
        """
            Rensar analysen och återställer vyn.
        """
        self.selected_competition = None
        self.selected_season = None
        self.selected_home_team = None
        self.selected_away_team = None

        self.seasons = []
        self.teams = []

        self.view.fill_competition_combo(self.competitions)

        self.view.fill_season_combo([])
        self.view.fill_team_combos([])

        self.view.competition_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.view.season_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.view.home_team_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.view.away_team_combo.setCurrentIndex(self.NO_ROW_SELECTED)
        self.view.enter_pre_analyze_state()
