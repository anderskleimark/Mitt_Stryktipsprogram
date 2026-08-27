from mvc import Controller


class BacktestController(Controller):
    """
        Controller för historisk backtestning
        av matchanalysmodellen.
    """
    TIME_DECAY_VALUES = (
        0.000,
        0.001,
        0.002,
        0.003,
        0.004,
        0.005,
        0.006,
        0.008,
        0.010
    )

    def __init__(
        self,
        *,
        view,
        backtest_model,
        competition_model,
        soccer_model
    ):
        super().__init__(view)

        self.view = view

        self.backtest_model = backtest_model
        self.competition_model = competition_model
        self.soccer_model = soccer_model

        self.competitions = []
        self.seasons = []

        self.selected_competition = None
        self.selected_season = None

        self._setup_signals()
        self.initialize()

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar vyens signaler till controllern.
        """
        self.view.competition_changed.connect(
            self.on_competition_changed
        )

        self.view.season_changed.connect(
            self.on_season_changed
        )

        self.view.run_clicked.connect(
            self.on_run_clicked
        )
        self.view.back_clicked.connect(
            self.on_back_clicked
        )

    def initialize(self):
        """
            Initierar vyn med tillgängliga
            tävlingar.
        """
        self.competitions = (
            self.competition_model.get_all()
        )

        self.view.fill_competition_combo(
            self.competitions
        )

        self._update_run_button()

    # --------------------------------------------------
    # Tävling
    # --------------------------------------------------

    def on_competition_changed(self):
        """
            Hanterar byte av tävling.
        """
        self.selected_competition = (
            self.view.get_selected_competition()
        )

        self.selected_season = None
        self.seasons = []

        self.view.clear_result()

        if self.selected_competition is None:
            self.view.fill_season_combo([])
            self._update_run_button()
            return

        self.seasons = (
            self.soccer_model.get_seasons(
                competition_id=(
                    self.selected_competition.id
                )
            )
        )

        self.view.fill_season_combo(
            self.seasons
        )

        self._update_run_button()

    # --------------------------------------------------
    # Säsong
    # --------------------------------------------------

    def on_season_changed(self):
        """
            Hanterar byte av säsong.
        """
        self.selected_season = (
            self.view.get_selected_season()
        )

        self.view.clear_result()

        if self.selected_season is not None:
            self.view.set_date_range(
                self._get_season_start_date(),
                self._get_season_end_date()
            )

        self._update_run_button()

    # --------------------------------------------------
    # Backtest
    # --------------------------------------------------

    def on_run_clicked(self):
        """
            Kör backtest med flera
            time-decay-värden.
        """
        if self.selected_season is None:
            return

        start_date = (
            self.view.get_start_date()
        )

        end_date = (
            self.view.get_end_date()
        )

        if start_date >= end_date:
            return

        self.view.set_run_button_status(
            False
        )

        try:
            results = (
                self.backtest_model
                .run_time_decay_comparison(
                    season=self.selected_season,
                    start_date=start_date,
                    end_date=end_date,
                    time_decay_values=self.TIME_DECAY_VALUES
                )
            )

            self.view.show_result(
                results
            )

        finally:
            self.view.set_run_button_status(
                True
            )

    def on_back_clicked(self):
        """
            Går tillbaka till inställningarna
            för backtestet.
        """
        self.view.show_settings()

    # --------------------------------------------------
    # Datum
    # --------------------------------------------------

    def _get_season_start_date(self):
        """
            Returnerar säsongens ungefärliga
            startdatum.
        """
        from datetime import date

        return date(
            self.selected_season.start_year,
            1,
            1
        )

    def _get_season_end_date(self):
        """
            Returnerar säsongens ungefärliga
            slutdatum.
        """
        from datetime import date

        return date(
            self.selected_season.end_year + 1,
            1,
            1
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def _update_run_button(self):
        """
            Uppdaterar status för
            backtestknappen.
        """
        self.view.set_run_button_status(
            self.selected_season is not None
        )
