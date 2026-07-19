from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from controllers.analysis_controller import AnalysisController
from controllers.bet_controller import BetController
from controllers.competition_controller import CompetitionController
from controllers.coupon_controller import CouponController
from controllers.create_own_system_controller import CreateOwnSystemController
from controllers.main_controller import MainController
from controllers.system_controller import SystemController
from database.database import Database
from models.analysis_model import AnalysisModel
from models.bet_model import BetModel
from models.competition_model import CompetitionModel
from models.coupon_model import CouponModel
from models.create_own_system_model import CreateOwnSystemModel
from models.system_model import SystemModel
from views.about_view import AboutView
from views.bet_view import BetView
from views.competition_view import CompetitionView
from views.coupon_view import CouponView
from views.coupon_analysis_view import CouponAnalysisView
from views.create_own_system_view import CreateOwnSystemView
from views.match_analysis_view import MatchAnalysisView
from views.start_view import StartView
from views.system_view import SystemView


class MainWindow(QMainWindow):

    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 700

    def __init__(self):
        super().__init__()

        style_file = Path(__file__).parent / "styles" / "styles.qss"
        if not style_file.exists():
            print(f"❌ Stylesheet hittades inte: {style_file}")
        else:
            with open(style_file, encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            print(f"✔ Stylesheet laddad: {style_file}")

        self.database = Database()
        self.setWindowTitle("Mitt stryktipsprogram")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self.stack = QStackedWidget()
        self.create_views()
        self.create_models()
        self.create_controllers()
        self.create_menu_system()

        self.setCentralWidget(self.stack)

    # Funktion för att skapa menysystemet.
    def create_menu_system(self):
        menu_bar = self.menuBar()

        # Arkivmenyn
        file_menu = menu_bar.addMenu("Arkiv")
        exit_action = QAction("Avsluta", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Verktygsmenyn
        tools_menu = menu_bar.addMenu("Verktyg")
        coupon_action = QAction("Kuponger", self)
        coupon_action.triggered.connect(
            lambda: self.main_controller.show_view("coupon_view")
        )
        tools_menu.addAction(coupon_action)

        system_action = QAction("System", self)
        tools_menu.addAction(system_action)
        system_action.triggered.connect(
            lambda: self.main_controller.show_view("system_view")
        )

        bet_action = QAction("Vad", self)
        tools_menu.addAction(bet_action)
        bet_action.triggered.connect(
            lambda: self.main_controller.show_view("bet_view")
        )

        create_own_system_action = QAction("Skapa ditt eget tipssystem", self)
        tools_menu.addAction(create_own_system_action)
        create_own_system_action.triggered.connect(
            lambda: self.main_controller.show_view("create_own_system_view")
        )

        # Meny med tävlingar/ligor, säsonger, lag med mera.
        competition_menu = menu_bar.addMenu("Tävlingar/ligor")
        competition_action = QAction("Tävlingar/ligor", self)
        competition_action.triggered.connect(
            lambda: self.main_controller.show_view("competition_view")
        )
        competition_menu.addAction(competition_action)

        # Meny för analys.
        analyze_menu = menu_bar.addMenu("Analys")
        single_match_analyze_action = QAction("Matchanalys", self)
        single_match_analyze_action.triggered.connect(
            lambda: self.main_controller.show_view("match_analysis_view")
        )
        analyze_menu.addAction(single_match_analyze_action)

        coupon_analysis_action = QAction("Kuponganalys", self)
        coupon_analysis_action.triggered.connect(
            lambda: self.main_controller.show_view("coupon_analysis_view")
        )
        analyze_menu.addAction(coupon_analysis_action)

        # Hjälpmenyn
        help_menu = menu_bar.addMenu("Hjälp")
        about_action = QAction("Om", self)
        about_action.triggered.connect(
            lambda: self.main_controller.show_view("about_view")
        )
        help_menu.addAction(about_action)

    # Funktion som skapar vyerna och lägger in dem i stackvyn.
    def create_views(self):
        self.views = {}

        # StartView
        self.views["start_view"] = StartView()

        # AboutView
        self.views["about_view"] = AboutView()

        # CouponView
        self.views["coupon_view"] = CouponView()

        # SystemView
        self.views["system_view"] = SystemView()

        # BetView
        self.views["bet_view"] = BetView()

        # CreateOwnSystemView
        self.views["create_own_system_view"] = CreateOwnSystemView()

        # CompetitionView
        self.views["competition_view"] = CompetitionView()

        # MatchAnalysisView
        self.views["match_analysis_view"] = MatchAnalysisView()

        # CouponAnalysisView
        self.views["coupon_analysis_view"] = CouponAnalysisView()

        for view in self.views.values():
            self.stack.addWidget(view)

    # Funktion för att skapa alla applikationens modeller.
    def create_models(self):
        self.coupon_model = CouponModel(self.database)
        self.system_model = SystemModel(self.database)
        self.bet_model = BetModel(self.database)
        self.create_own_system_model = CreateOwnSystemModel()
        self.competion_model = CompetitionModel(self.database)
        self.analysis_model = AnalysisModel()

    # Funktion för att skapa alla applikationens kontrollklasser.
    def create_controllers(self):
        self.main_controller = MainController(None, self)
        self.coupon_controller = CouponController(
            self.coupon_model, self.views["coupon_view"])
        self.system_controller = SystemController(
            self.system_model, self.views["system_view"])
        self.bet_controller = BetController(
            self.bet_model, self.coupon_model, self.system_model, self.views["bet_view"])
        self.create_own_system_controller = CreateOwnSystemController(
            self.create_own_system_model, self.views["create_own_system_view"])
        self.competition_controller = CompetitionController(
            self.competion_model, self.views["competition_view"])
        self.analysis_controller = AnalysisController(
            self.analysis_model,
            self.views["match_analysis_view"],
            self.views["coupon_analysis_view"]
        )
