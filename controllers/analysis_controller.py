from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from mvc import Controller
from datetime import date


class AnalysisController(Controller):
    """
        Controller som hanterar analys av fotbollsmatcher.

        Controllern hanterar val av tävling, säsong och lag samt start och navigering
        av matchanalysen.
    """

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
            Initierar controllern med modeller och tillhörande vyer.
        """
        super().__init__(match_view)

        self.analysis_model = analysis_model
        self.competition_model = competition_model
        self.soccer_model = soccer_model
        self.coupon_view = coupon_view

        # Tävlingar, säsonger och lag.
        self.competitions = []
        self.seasons = []
        self.teams = []

        # Aktuella val.
        self.selected_competition = None
        self.selected_season = None
        self.selected_home_team = None
        self.selected_away_team = None

        self.add_connections()
        self.load_competitions()
        self.view.enter_pre_analyze_state()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def add_connections(self):
        """
            Kopplar signaler från vyn till controllerns händelsemetoder.
        """
        self.view.competition_changed.connect(
            self.on_selected_competition_changed
        )

        self.view.season_changed.connect(
            self.on_selected_season_changed
        )

        self.view.home_team_changed.connect(
            self.on_selected_home_team_changed
        )

        self.view.away_team_changed.connect(
            self.on_selected_away_team_changed
        )

        self.view.analyze_clicked.connect(
            self.on_analyze_match_clicked
        )

        self.view.statistics_clicked.connect(
            self.on_statistics_button_clicked
        )

        self.view.dixon_coles_clicked.connect(
            self.on_dixon_coles_button_clicked
        )

        self.view.probability_clicked.connect(
            self.on_probability_button_clicked)

        self.view.odds_clicked.connect(self.on_odds_button_clicked)
        self.view.clear_clicked.connect(self.on_clear_analysis_clicked)

    # --------------------------------------------------
    # Inläsning
    # --------------------------------------------------

    def load_competitions(self):
        """
            Hämtar och visar tillgängliga tävlingar.
        """
        self.competitions = self.competition_model.get_all()
        self.view.fill_competition_combo(self.competitions)

    # --------------------------------------------------
    # Val av tävling, säsong och lag
    # --------------------------------------------------

    def on_selected_competition_changed(self):
        """
            Hanterar byte av vald tävling.
        """
        row = self.view.get_selected_competition_row()

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
        row = self.view.get_selected_season_row()

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

        self.view.fill_team_combos(self.teams)

        self.update_buttons()

    def on_selected_home_team_changed(self):
        """
            Hanterar byte av valt hemmalag.
        """
        self.selected_home_team = self.view.get_selected_home_team()

        self.update_away_team_combo()
        self.update_buttons()

    def on_selected_away_team_changed(self):
        """
            Hanterar byte av valt bortalag.
        """
        self.selected_away_team = self.view.get_selected_away_team()

        self.update_buttons()

    def get_available_away_teams(self):
        """
            Returnerar de lag som kan väljas som bortalag.
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
        self.view.fill_away_team_combo(teams)

    # --------------------------------------------------
    # Analys
    # --------------------------------------------------

    def on_analyze_match_clicked(self):
        """
            Genomför analys av vald match och visar
            resultatet i analysvyn.

            Kör även tillfälligt ett mindre backtest
            för att kontrollera modellens historiska
            prognoser.
        """
        if (
            self.selected_season is None
            or self.selected_home_team is None
            or self.selected_away_team is None
        ):
            return

        try:
            analysis = self.analysis_model.analyze_match(
                season=self.selected_season,
                home_team=self.selected_home_team,
                away_team=self.selected_away_team
            )

            self.view.show_analysis(
                analysis
            )

            # --------------------------------------------------
            # Tillfälligt backtest
            # --------------------------------------------------

            self.view.enter_view_state()

        except (
            ValueError,
            RuntimeError
        ) as error:
            print(
                f"Matchanalysen misslyckades: {error}"
            )

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def on_statistics_button_clicked(self):
        """
        Visar statistiksidan.
        """
        self.view.show_statistics()

    def on_dixon_coles_button_clicked(self):
        """
            Visar Dixon-Coles-sidan.
        """
        self.view.show_dixon_coles()

    def on_probability_button_clicked(self):
        """
            Visar sannolikhetssidan.
        """
        self.view.show_probabilities()

    def on_odds_button_clicked(self):
        """
            Visar oddssidan.
        """
        self.view.show_odds()

    # --------------------------------------------------
    # Knappar
    # --------------------------------------------------

    def update_buttons(self):
        """
            Uppdaterar analys- och rensningsknapparna utifrån aktuella val.
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

        self.view.set_analyze_button_status(ready)
        self.view.set_clear_button_status(has_selection)

    # --------------------------------------------------
    # Rensning
    # --------------------------------------------------

    def on_clear_analysis_clicked(self):
        """
            Rensar analysen och återställer samtliga val.
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

        self.view.reset_match_selection()
        self.view.enter_pre_analyze_state()

    def run_backtest(self):
        """
            Kör ett mindre backtest för att kontrollera
            att backtestkedjan fungerar.
        """
        result = self.backtest_model.run(
            season=self.selected_season,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 15)
        )
