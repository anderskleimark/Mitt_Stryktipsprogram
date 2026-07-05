from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtGui import QAction
from views.about_view import AboutView
from views.coupon_view import CouponView
from views.start_view import StartView
from views.system_view import SystemView
from views.create_own_system_view import CreateOwnSystemView
from views.bet_view import BetView
from models.coupon_model import CouponModel
from models.system_model import SystemModel
from models.bet_model import BetModel
from models.create_own_system_model import CreateOwnSystemModel
from controllers.main_controller import MainController
from controllers.coupon_controller import CouponController
from controllers.system_controller import SystemController
from controllers.bet_controller import BetController
from controllers.create_own_system_controller import CreateOwnSystemController
from database.database import Database
from pathlib import Path


class MainWindow(QMainWindow):

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
        self.resize(800, 600)

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

        for view in self.views.values():
            self.stack.addWidget(view)

    # Funktion för att skapa alla applikationens modeller.
    def create_models(self):
        self.coupon_model = CouponModel(self.database)
        self.system_model = SystemModel(self.database)
        self.bet_model = BetModel(self.database)
        self.create_own_system_model = CreateOwnSystemModel()

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
