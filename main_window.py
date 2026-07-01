from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtGui import QAction
from views.about_view import AboutView
from views.show_coupons_view import ShowCouponsView
from views.start_view import StartView
from views.add_coupon_view import AddCouponView
from views.system_view import SystemView
from views.bet_view import BetView
from models.coupon_model import CouponModel
from models.system_model import SystemModel
from models.bet_model import BetModel
from controllers.add_coupon_controller import AddCouponController
from controllers.main_controller import MainController
from controllers.show_coupons_controller import ShowCouponsController
from controllers.system_controller import SystemController
from controllers.bet_controller import BetController
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

        # Tabell-menyn

        # Kupongmenyn
        result_menu = menu_bar.addMenu("Kuponger")
        result_action = QAction("Kuponger", self)
        result_action.triggered.connect(
            lambda: self.main_controller.show_view("show_coupons_view")
        )
        result_menu.addAction(result_action)

        # Spel-menyn
        game_menu = menu_bar.addMenu("Spel")
        system_action = QAction("System", self)
        game_menu.addAction(system_action)
        system_action.triggered.connect(
            lambda: self.main_controller.show_view("system_view")
        )
        game_history_action = QAction("Historik", self)
        game_menu.addAction(game_history_action)
        game_history_action.triggered.connect(
            lambda: self.main_controller.show_view("bet_view")
        )

        # Verktygsmenyn
        tools_menu = menu_bar.addMenu("Verktyg")
        add_coupon_action = QAction("Lägg till en kupong", self)
        tools_menu.addAction(add_coupon_action)
        add_coupon_action.triggered.connect(
            lambda: self.main_controller.show_view("add_coupon_view")
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

        # ShowCouponsView
        self.views["show_coupons_view"] = ShowCouponsView()

        # AddCouponView
        self.views["add_coupon_view"] = AddCouponView()

        # SystemView
        self.views["system_view"] = SystemView()

        # Historik
        self.views["bet_view"] = BetView()

        for view in self.views.values():
            self.stack.addWidget(view)

    # Funktion för att skapa alla applikationens modeller.
    def create_models(self):
        self.coupon_model = CouponModel(self.database)
        self.system_model = SystemModel(self.database)
        self.bet_model = BetModel(self.database)

    # Funktion för att skapa alla applikationens kontrollklasser.
    def create_controllers(self):
        self.main_controller = MainController(None, self)
        self.add_coupon_controller = AddCouponController(
            self.coupon_model, self.views["add_coupon_view"])
        self.show_coupons_controller = ShowCouponsController(
            self.coupon_model, self.views["show_coupons_view"])
        self.system_controller = SystemController(
            self.system_model, self.views["system_view"])
        self.bet_controller = BetController(
            self.bet_model, self.coupon_model, self.system_model, self.views["bet_view"])
