from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtGui import QAction
from views.about_view import AboutView
from views.result_view import ResultView
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

    def create_menu_system(self):
        menu_bar = self.menuBar()

        # FileMenu
        file_menu = menu_bar.addMenu("Arkiv")
        exit_action = QAction("Avsluta", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tabell-menyn

        # Resultatmenyn
        result_menu = menu_bar.addMenu("Resultat")
        result_action = QAction("Resultat", self)
        result_action.triggered.connect(
            self.main_controller.show_result_view
        )
        result_menu.addAction(result_action)

        # Hjälpmenyn
        help_menu = menu_bar.addMenu("Hjälp")

    def create_views(self):
        self.about_view = AboutView()
        self.result_view = ResultView()
        self.stack.addWidget(self.about_view)
        self.stack.addWidget(self.result_view)

    def create_controllers(self):
        self.main_controller = MainController(None, self)
