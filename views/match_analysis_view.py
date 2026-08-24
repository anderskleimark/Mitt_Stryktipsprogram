from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QStackedWidget, QWidget

from mvc import View
from widgets.analysis_navigation_widget import AnalysisNavigationWidget
from widgets.dixon_coles_widget import DixonColesWidget
from widgets.match_selection_widget import MatchSelectionWidget
from widgets.match_statistics_widget import MatchStatisticsWidget
from widgets.probability_widget import ProbabilityWidget


class MatchAnalysisView(View):
    """
        Vy för att visa och hantera analys av en fotbollsmatch.

        Vyn innehåller matchval, separata analyssidor
        för statistik, Dixon-Coles, sannolikheter och
        odds samt navigering mellan analyssidorna.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()
    season_changed = Signal()
    home_team_changed = Signal()
    away_team_changed = Signal()

    analyze_clicked = Signal()
    clear_clicked = Signal()

    statistics_clicked = Signal()
    dixon_coles_clicked = Signal()
    probability_clicked = Signal()
    odds_clicked = Signal()

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Matchanalys"
    LABEL_ODDS = "Oddsanalys"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    ANALYSIS_PAGE_SPACING = 1

    def __init__(self):
        """
            Initierar vyn och skapar matchval, analyssidor, navigering och signaler.
        """
        super().__init__()

        # Sidor/widgets
        self.statistics_widget = None
        self.dixon_coles_widget = None
        self.probability_widget = None
        self.odds_page = None

        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.match_selection_widget = MatchSelectionWidget()
        self.layout.addWidget(self.match_selection_widget)

        self.create_separator()
        self.create_analysis_widget()

        self.navigation_widget = AnalysisNavigationWidget()
        self.add_bottom_panel(self.navigation_widget)

        self.setLayout(self.layout)
        self._setup_signals()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Vidarebefordrar signaler från underliggande widgetar genom vyklassens egna signaler.
        """
        self.match_selection_widget.competition_changed.connect(
            self.competition_changed.emit
        )

        self.match_selection_widget.season_changed.connect(
            self.season_changed.emit)

        self.match_selection_widget.home_team_changed.connect(
            self.home_team_changed.emit
        )

        self.match_selection_widget.away_team_changed.connect(
            self.away_team_changed.emit
        )

        self.match_selection_widget.analyze_clicked.connect(
            self.analyze_clicked.emit
        )

        self.match_selection_widget.clear_clicked.connect(
            self.clear_clicked.emit)

        self.navigation_widget.statistics_clicked.connect(
            self.statistics_clicked.emit)

        self.navigation_widget.dixon_coles_clicked.connect(
            self.dixon_coles_clicked.emit)

        self.navigation_widget.probability_clicked.connect(
            self.probability_clicked.emit)

        self.navigation_widget.odds_clicked.connect(self.odds_clicked.emit)

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_separator(self):
        """
            Skapar den horisontella avskiljaren mellan matchvalet och analysytan.
        """
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.layout.addWidget(self.separator)

    def create_analysis_widget(self):
        """
            Skapar analysytan och dess underliggande analyssidor.
        """
        self.analysis_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.analysis_widget,
            spacing=self.ANALYSIS_PAGE_SPACING
        )

        self.analysis_stack = QStackedWidget()

        self.create_statistics_page()
        self.create_dixon_coles_page()
        self.create_probability_page()
        self.create_odds_page()

        layout.addWidget(self.analysis_stack)

        self.layout.addWidget(
            self.analysis_widget,
            stretch=self.FULL_STRETCH
        )

    def create_statistics_page(self):
        """
            Skapar sidan för matchstatistik.
        """
        self.statistics_widget = MatchStatisticsWidget()
        self.analysis_stack.addWidget(self.statistics_widget)

    def create_dixon_coles_page(self):
        """
            Skapar sidan för Dixon-Coles-analys.
        """

        self.dixon_coles_widget = DixonColesWidget()
        self.analysis_stack.addWidget(self.dixon_coles_widget)

    def create_probability_page(self):
        """
            Skapar sidan för sannolikhetsanalys.
        """
        self.probability_widget = ProbabilityWidget()
        self.analysis_stack.addWidget(self.probability_widget)

    def create_odds_page(self):
        """
            Skapar sidan för oddsanalys.
        """
        self.odds_page = QWidget()

        layout = self.create_vertical_layout(
            parent=self.odds_page,
            spacing=None
        )

        label = QLabel(self.LABEL_ODDS)
        label.setAlignment(label.alignment())

        layout.addWidget(label)

        self.analysis_stack.addWidget(self.odds_page)

    # --------------------------------------------------
    # Navigering
    # --------------------------------------------------

    def show_statistics(self):
        """
            Visar statistiksidan.
        """
        self.analysis_stack.setCurrentWidget(self.statistics_widget)

    def show_dixon_coles(self):
        """
            Visar Dixon-Coles-sidan.
        """
        self.analysis_stack.setCurrentWidget(self.dixon_coles_widget)

    def show_probabilities(self):
        """
            Visar sannolikhetssidan.
        """
        self.analysis_stack.setCurrentWidget(self.probability_widget)

    def show_odds(self):
        """
            Visar oddssidan.
        """
        self.analysis_stack.setCurrentWidget(self.odds_page)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar resultatet från en genomförd matchanalys i samtliga analyssidor.
        """
        self.statistics_widget.show_analysis(analysis)
        self.dixon_coles_widget.show_analysis(analysis)
        self.probability_widget.show_analysis(analysis)

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def enter_pre_analyze_state(self):
        """
            Återställer vyn inför en ny matchanalys.

            Tidigare analysresultat och val rensas och navigeringen inaktiveras.
        """
        self.clear_analysis()
        self.enable_navigation(False)

        self.set_competition_combo_status(True)
        self.set_season_combo_status(True)
        self.set_home_team_combo_status(True)
        self.set_away_team_combo_status(True)

        self.set_analyze_button_status(False)
        self.set_clear_button_status(False)

        self.reset_match_selection()
        self.show_statistics()

    def enter_view_state(self):
        """
            Växlar vyn till läget efter en genomförd analys.

            Navigeringen och rensningsknappen aktiveras.
        """
        self.enable_navigation(True)
        self.set_clear_button_status(True)

    def clear_analysis(self):
        """
            Tömmer samtliga resultat från föregående matchanalys.
        """
        self.statistics_widget.clear_analysis()
        self.dixon_coles_widget.clear_analysis()
        self.probability_widget.clear_analysis()

    def enable_navigation(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar navigeringspanelen.
        """
        self.navigation_widget.set_enabled(status)

    # --------------------------------------------------
    # Delegationsmetoder - innehåll
    # --------------------------------------------------

    def fill_competition_combo(
        self,
        competitions=None
    ):
        """
            Fyller tävlingslistan i matchvalswidgeten.
        """
        self.match_selection_widget.fill_competition_combo(competitions)

    def fill_season_combo(
        self,
        seasons=None
    ):
        """
            Fyller säsongslistan i matchvalswidgeten.
        """
        self.match_selection_widget.fill_season_combo(seasons)

    def fill_team_combos(
        self,
        teams
    ):
        """
            Fyller listorna för hemma- och bortalag.
        """
        self.match_selection_widget.fill_team_combos(teams)

    def fill_home_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med tillgängliga hemmalag.
        """
        self.match_selection_widget.fill_home_team_combo(teams)

    def fill_away_team_combo(
        self,
        teams=None
    ):
        """
            Fyller listan med tillgängliga bortalag.
        """
        self.match_selection_widget.fill_away_team_combo(teams)

    # --------------------------------------------------
    # Delegationsmetoder - status
    # --------------------------------------------------

    def set_competition_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar tävlingslistan.
        """
        self.match_selection_widget.set_competition_combo_status(status)

    def set_season_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar säsongslistan.
        """
        self.match_selection_widget.set_season_combo_status(status)

    def set_home_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar hemmalagslistan.
        """
        self.match_selection_widget.set_home_team_combo_status(status)

    def set_away_team_combo_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar bortalagslistan.
        """
        self.match_selection_widget.set_away_team_combo_status(status)

    def set_analyze_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar analysknappen.
        """
        self.match_selection_widget.set_analyze_button_status(status)

    def set_clear_button_status(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar rensningsknappen.
        """
        self.match_selection_widget.set_clear_button_status(status)

    # --------------------------------------------------
    # Delegationsmetoder - val
    # --------------------------------------------------

    def get_selected_competition_row(self):
        """
            Returnerar index för vald tävling.

            Returnerar -1 om ingen tävling är vald.
        """
        return self.match_selection_widget.get_selected_competition_row()

    def get_selected_season_row(self):
        """
            Returnerar index för vald säsong.

            Returnerar -1 om ingen säsong är vald.
        """
        return self.match_selection_widget.get_selected_season_row()

    def get_selected_home_team(self):
        """
            Returnerar valt hemmalags Team-objekt.

            Returnerar None om inget hemmalag är valt.
        """
        return self.match_selection_widget.get_selected_home_team()

    def get_selected_away_team(self):
        """
            Returnerar valt bortalags Team-objekt.
            Returnerar None om inget bortalag är valt.
        """
        return self.match_selection_widget.get_selected_away_team()

    def reset_match_selection(self):
        """
            Återställer samtliga val i matchvalswidgeten.
        """
        self.match_selection_widget.reset()
