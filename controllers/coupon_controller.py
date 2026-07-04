from PySide6.QtWidgets import QMessageBox
from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from models.coupon_model import Game

# En Controller-klass, som samarbetar med vyn som visar tillagda tipskuponger.


class CouponController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()
        self.load_coupon()
        self.view.enter_view_mode()

    def add_connections(self):
        self.view.year_week_widget.year_week_changed.connect(
            self.on_year_week_changed)
        self.view.save_button.clicked.connect(self.on_save_button_clicked)
        self.view.add_coupon_button.clicked.connect(self.on_add_coupon_clicked)
        self.view.back_button.clicked.connect(self.on_back_button_clicked)
        self.view.print_button.clicked.connect(self.on_print_clicked)
        self.view.delete_button.clicked.connect(self.on_delete_clicked)
        self.view.game_table.itemChanged.connect(self.on_item_changed)

    # Funktion som körs, om året eller veckan ändras.
    def on_year_week_changed(self, year, week):
        self.load_coupon()

    # Funktion som körs, om någonting ändras i tabellen.
    def on_item_changed(self, item):
        row = item.row()
        col = item.column()

        # Endast resultatkolumnerna
        if col not in (2, 3):
            return

        home_item = self.view.game_table.item(row, 2)
        away_item = self.view.game_table.item(row, 3)

        if home_item is None or away_item is None:
            return

        try:
            home_score = int(home_item.text().strip())
            away_score = int(away_item.text().strip())
        except ValueError:
            return

        coupon = self.model.current_coupon
        if coupon is None:
            return

        # Hämta Game-objektet
        game = coupon.games[row]

        # Uppdatera objektet
        game.home_score = home_score
        game.away_score = away_score

        # Spara i databasen
        self.model.update_game_score(
            coupon.id,
            game.number,
            home_score,
            away_score
        )

        # Uppdatera endast 1X2-kolumnen
        self.view.game_table.blockSignals(True)

        result_item = self.view.game_table.item(row, 4)

        if result_item is None:
            result_item = QTableWidgetItem()
            self.view.game_table.setItem(row, 4, result_item)

        result_item.setText(game.result_1x2)
        self.view.game_table.blockSignals(False)

    # Funktion för att spara en tipskupong.
    def on_save_button_clicked(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        games = self.view.get_games()

        # validering
        for game in games:

            if not game.home_team:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    f"Hemmalag saknas i match {game.number}."
                )
                return

            if not game.away_team:
                QMessageBox.warning(
                    self.view,
                    "Fel",
                    f"Bortalag saknas i match {game.number}."
                )
                return

        self.model.create_coupon_with_games(
            year,
            week,
            games
        )
        self.view.clear_form()

    # Funktion för att visa formuläret för att lägga till en tipskupong.
    def on_add_coupon_clicked(self):
        self.view.enter_create_mode()

    # Funktion för att komma till "visaläget".
    def on_back_button_clicked(self):
        self.view.enter_view_mode()

    # Funktion som hanterar händelser, om använder trycker på "Skriv ut".
    def on_print_clicked(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_by_year_week(year, week)

        if coupon is None:
            return

        document = QTextDocument()
        document.setHtml(
            self.create_coupon_html(coupon)
        )

        printer = QPrinter()
        dialog = QPrintDialog(printer, self.view)

        if dialog.exec():
            document.print_(printer)

    # Funktion för interaktion, om användaren trycker på "radera".
    def on_delete_clicked(self):
        message = QMessageBox(self.view)
        message.setIcon(QMessageBox.Icon.Warning)
        message.setWindowTitle("Radera kupong")
        message.setText("Är du säker på att du vill radera kupongen?")
        message.setInformativeText("Denna åtgärd kan inte ångras.")
        message.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        message.setDefaultButton(QMessageBox.StandardButton.Cancel)

        reply = message.exec()
        if reply == QMessageBox.StandardButton.Ok:
            print("OK")
        else:
            print("Avbryt")

    # Funktion som har hand om skapandet av den html som behövs vid utskrift av kuponger.

    def create_coupon_html(self, coupon):

        html = f"""
        <h1>Stryktipskupong</h1>

        <p>
            <b>År:</b> {coupon.year}<br>
            <b>Omgång:</b> {coupon.week}
        </p>

        <table border="1" cellspacing="0" cellpadding="5" width="100%">

            <tr>
                <th>Nr</th>
                <th>Hemmalag</th>
                <th>Bortalag</th>
                <th>Resultat</th>
            </tr>
        """

        for game in coupon.games:

            html += f"""
            <tr>
                <td>{game.number}</td>
                <td>{game.home_team}</td>
                <td>{game.away_team}</td>
                <td>{game.result_1x2}</td>
            </tr>
            """

        html += "</table>"

        return html

    # Funktion för att ladda en tipskupong utifrån vad som har valts i vyn.
    def load_coupon(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_by_year_week(year, week)

        if coupon is None:
            self.view.set_buttons_enabled(False)
            self.view.update_games([])
            return

        self.model.current_coupon = coupon
        self.view.update_games(coupon.games)
        self.view.set_buttons_enabled(True)

        self.view.game_table.blockSignals(True)
        self.view.update_games(coupon.games)
        self.view.game_table.blockSignals(False)

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.view.clear_form()
