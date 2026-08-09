from functools import partial
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from controllers.analysis_controller import AnalysisController
from controllers.bet_controller import BetController
from controllers.competition_controller import CompetitionController
from controllers.coupon_controller import CouponController
from controllers.create_own_system_controller import CreateOwnSystemController
from controllers.main_controller import MainController
from controllers.setting_controller import SettingController
from controllers.system_controller import SystemController
from controllers.team_controller import TeamController
from database.database import Database
from models.analysis_model import AnalysisModel
from models.bet_model import BetModel
from models.competition_model import CompetitionModel
from models.country_model import CountryModel
from models.coupon_model import CouponModel
from models.create_own_system_model import CreateOwnSystemModel
from models.setting_model import SettingModel
from models.soccer_model import SoccerModel
from models.system_model import SystemModel
from models.team_model import TeamModel
from views.about_view import AboutView
from views.bet_view import BetView
from views.competition_view import CompetitionView
from views.coupon_analysis_view import CouponAnalysisView
from views.coupon_view import CouponView
from views.create_own_system_view import CreateOwnSystemView
from views.match_analysis_view import MatchAnalysisView
from views.setting_view import SettingView
from views.start_view import StartView
from views.system_view import SystemView
from views.team_view import TeamView


class MainWindow(QMainWindow):
    """
        Applikationens huvudfönster.

        Hanterar vyer, modeller, controllers och menyer.
    """

    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 700

    def __init__(self):
        """
            Initierar huvudfönstret.
        """
        super().__init__()

        style_file = (
            Path(__file__).parent
            / "styles"
            / "styles.qss"
        )

        if not style_file.exists():
            print(
                f"❌ Stylesheet hittades inte: {style_file}"
            )
        else:
            with open(
                style_file,
                encoding="utf-8"
            ) as file:
                self.setStyleSheet(
                    file.read()
                )

            print(
                f"✔ Stylesheet laddad: {style_file}"
            )

        self.database = Database()

        self.setWindowTitle(
            "Mitt stryktipsprogram"
        )

        self.resize(
            self.DEFAULT_WIDTH,
            self.DEFAULT_HEIGHT
        )

        self.stack = QStackedWidget()

        self.create_views()
        self.create_models()
        self.create_controllers()
        self.create_menu_system()

        self.setCentralWidget(
            self.stack
        )

    def create_menu_system(self):
        """
            Skapar applikationens menysystem.
        """
        menu_bar = self.menuBar()

        # Arkivmenyn
        file_menu = menu_bar.addMenu(
            "Arkiv"
        )

        exit_action = QAction(
            "Avsluta",
            self
        )

        exit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(
            exit_action
        )

        # Verktygsmenyn
        tools_menu = menu_bar.addMenu(
            "Verktyg"
        )

        self.add_view_action(
            tools_menu,
            "Lag",
            "team_view"
        )

        self.add_view_action(
            tools_menu,
            "Kuponger",
            "coupon_view"
        )

        self.add_view_action(
            tools_menu,
            "System",
            "system_view"
        )

        self.add_view_action(
            tools_menu,
            "Vad",
            "bet_view"
        )

        self.add_view_action(
            tools_menu,
            "Skapa ditt eget tipssystem",
            "create_own_system_view"
        )

        # Meny med tävlingar/ligor.
        competition_menu = menu_bar.addMenu(
            "Tävlingar/ligor"
        )

        self.add_view_action(
            competition_menu,
            "Tävlingar/ligor",
            "competition_view"
        )

        # Analysmenyn
        analyze_menu = menu_bar.addMenu(
            "Analys"
        )

        self.add_view_action(
            analyze_menu,
            "Matchanalys",
            "match_analysis_view"
        )

        self.add_view_action(
            analyze_menu,
            "Kuponganalys",
            "coupon_analysis_view"
        )

        # Inställningsmenyn
        setting_menu = menu_bar.addMenu(
            "Inställningar"
        )

        self.add_view_action(
            setting_menu,
            "Inställningar",
            "setting_view"
        )

        # Hjälpmenyn
        help_menu = menu_bar.addMenu(
            "Hjälp"
        )

        self.add_view_action(
            help_menu,
            "Om",
            "about_view"
        )

    def create_views(self):
        """
            Skapar och registrerar applikationens vyer.
        """
        self.views = {}

        self.views["start_view"] = StartView()
        self.views["about_view"] = AboutView()
        self.views["team_view"] = TeamView()
        self.views["coupon_view"] = CouponView()
        self.views["system_view"] = SystemView()
        self.views["bet_view"] = BetView()

        self.views["create_own_system_view"] = (
            CreateOwnSystemView()
        )

        self.views["competition_view"] = (
            CompetitionView()
        )

        self.views["match_analysis_view"] = (
            MatchAnalysisView()
        )

        self.views["coupon_analysis_view"] = (
            CouponAnalysisView()
        )

        self.views["setting_view"] = SettingView()

        for view in self.views.values():
            self.stack.addWidget(
                view
            )

    def create_models(self):
        """
            Skapar applikationens modeller.
        """
        self.coupon_model = CouponModel(
            self.database
        )

        self.system_model = SystemModel(
            self.database
        )

        self.bet_model = BetModel(
            self.database
        )

        self.create_own_system_model = (
            CreateOwnSystemModel()
        )

        self.competion_model = CompetitionModel(
            self.database
        )

        self.soccer_model = SoccerModel(
            self.database
        )

        self.analysis_model = AnalysisModel(
            self.database,
            self.soccer_model
        )

        self.team_model = TeamModel(
            self.database
        )

        self.country_model = CountryModel(
            self.database
        )

        self.setting_model = SettingModel(
            self.database
        )

    def create_controllers(self):
        """
            Skapar applikationens controllers.
        """
        self.coupon_controller = CouponController(
            coupon_model=self.coupon_model,
            soccer_model=self.soccer_model,
            team_model=self.team_model,
            view=self.views["coupon_view"]
        )

        self.system_controller = SystemController(
            system_model=self.system_model,
            view=self.views["system_view"]
        )

        self.bet_controller = BetController(
            bet_model=self.bet_model,
            coupon_model=self.coupon_model,
            system_model=self.system_model,
            view=self.views["bet_view"]
        )

        self.create_own_system_controller = (
            CreateOwnSystemController(
                create_own_system_model=(
                    self.create_own_system_model
                ),
                view=self.views[
                    "create_own_system_view"
                ]
            )
        )

        self.competition_controller = (
            CompetitionController(
                competition_model=(
                    self.competion_model
                ),
                soccer_model=self.soccer_model,
                country_model=self.country_model,
                view=self.views[
                    "competition_view"
                ]
            )
        )

        self.analysis_controller = AnalysisController(
            analysis_model=self.analysis_model,
            competition_model=(
                self.competion_model
            ),
            soccer_model=self.soccer_model,
            match_view=self.views[
                "match_analysis_view"
            ],
            coupon_view=self.views[
                "coupon_analysis_view"
            ]
        )

        self.team_controller = TeamController(
            team_model=self.team_model,
            country_model=self.country_model,
            view=self.views["team_view"]
        )

        self.setting_controller = SettingController(
            setting_model=self.setting_model,
            view=self.views["setting_view"],
            main_window=self
        )

        # MainController skapas sist eftersom den
        # behöver tillgång till övriga controllers.
        self.main_controller = MainController(
            self
        )

    def add_view_action(
        self,
        menu,
        text,
        view_name
    ):
        """
            Lägger till en menyåtgärd som visar en vy.
        """
        action = QAction(
            text,
            self
        )

        action.triggered.connect(
            partial(
                self.main_controller.show_view,
                view_name
            )
        )

        menu.addAction(
            action
        )

        return action

    def apply_font(
        self,
        font
    ):
        """
            Applicerar typsnittet på huvudfönstret och menyn.
        """
        self.setFont(
            font
        )

        menu_bar = self.menuBar()

        menu_bar.setFont(
            font
        )

        for action in menu_bar.actions():
            menu = action.menu()

            if menu is not None:
                menu.setFont(
                    font
                )

        self.update()
