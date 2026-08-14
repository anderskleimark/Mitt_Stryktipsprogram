import locale
import sqlite3
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from main_window import MainWindow


class App:
    ICON_PATH = "resources/icons/app.png"
    SWEDISH_LOCALE = "sv_SE.UTF-8"

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(
            QIcon(self.ICON_PATH)
        )
        locale.setlocale(locale.LC_COLLATE, self.SWEDISH_LOCALE)
        self.window = MainWindow()

    def run(self):
        self.window.show()
        return self.app.exec()


if __name__ == "__main__":
    try:
        app = App()

    except sqlite3.OperationalError as error:
        if "database is locked" in str(error).lower():
            QMessageBox.critical(
                None,
                "Databasen är låst",
                "Databasen används av ett annat program.\n\n"
                "Stäng programmet som använder databasen "
                "och försök igen."
            )
            sys.exit(1)
        raise

    sys.exit(app.run())
