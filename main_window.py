from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtGui import QAction
from views.about_view import AboutView
from views.show_coupons_view import ShowCouponsView
from views.start_view import StartView
from views.add_coupon_view import AddCouponView
from models.coupon_model import CouponModel
from controllers.add_coupon_controller import AddCouponController
from controllers.main_controller import MainController
from controllers.show_coupons_controller import ShowCouponsController
from database.database import Database


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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

        # ResultView
        self.views["show_coupons_view"] = ShowCouponsView()

        # AddCouponView
        self.views["add_coupon_view"] = AddCouponView()

        for view in self.views.values():
            self.stack.addWidget(view)

    # Funktion för att skapa alla applikationens modeller.
    def create_models(self):
        self.coupon_model = CouponModel(self.database)

    # Funktion för att skapa alla applikationens kontrollklasser.
    def create_controllers(self):
        self.main_controller = MainController(None, self)
        self.add_coupon_controller = AddCouponController(
            self.coupon_model, self.views["add_coupon_view"])
        self.show_coupons_controller = ShowCouponsController(
            self.coupon_model, self.views["show_coupons_view"])
