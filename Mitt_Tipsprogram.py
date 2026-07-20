import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
import locale


class App:

    def __init__(self):
        self.app = QApplication(sys.argv)
        locale.setlocale(locale.LC_COLLATE, "sv_SE.UTF-8")
        self.window = MainWindow()

    def run(self):
        self.window.show()
        return self.app.exec()


if __name__ == "__main__":
    app = App()
    sys.exit(app.run())
