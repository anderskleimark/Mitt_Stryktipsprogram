from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtGui import QAction
from views.about_view import AboutView
from views.result_view import ResultView
from views.start_view import StartView
from controllers.main_controller import MainController


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mitt stryktipsprogram")
        self.resize(800, 600)

        self.stack = QStackedWidget()
        self.create_views()
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

        # Resultatmenyn
        result_menu = menu_bar.addMenu("Resultat")
        result_action = QAction("Resultat", self)
        result_action.triggered.connect(
            lambda: self.main_controller.show_view("result_view")
        )
        result_menu.addAction(result_action)

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
        self.views["result_view"] = ResultView()

        for view in self.views.values():
            self.stack.addWidget(view)

    def create_controllers(self):
        self.main_controller = MainController(None, self)
