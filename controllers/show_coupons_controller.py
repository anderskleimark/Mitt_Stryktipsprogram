from PySide6.QtWidgets import QMessageBox
from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidgetItem

# En Controller-klass, som samarbetar med vyn som visar tillagda tipskuponger.


class ShowCouponsController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()
        self.load_coupon()

    def add_connections(self):
        self.view.year_week_widget.year_week_changed.connect(
            self.on_year_week_changed
        )
        self.view.print_button.clicked.connect(
            self.on_print_clicked
        )
        self.view.game_table.itemChanged.connect(self.on_item_changed)

    def on_year_week_changed(self, year, week):
        self.load_coupon()

    def on_item_changed(self, item):
        row = item.row()
        col = item.column()

        if col not in (2, 3):
            return

        home_item = self.view.game_table.item(row, 2)
        away_item = self.view.game_table.item(row, 3)

        if home_item is None or away_item is None:
            return

        try:
            home_text = home_item.text().strip()
            away_text = away_item.text().strip()

            # viktigt: tillåt 0
            home_score = int(home_text)
            away_score = int(away_text)

        except ValueError:
            return

        coupon = self.model.current_coupon
        if coupon is None:
            return

        game = coupon.games[row]

        game.home_score = home_score
        game.away_score = away_score

        self.model.update_game_score(
            coupon.id,
            game.number,
            home_score,
            away_score
        )

        # ✔ ENDAST uppdatera 1 cell (inte hela tabellen)
        result_item = QTableWidgetItem(game.result_1x2)

        self.view.game_table.blockSignals(True)
        self.view.game_table.setItem(row, 4, result_item)
        self.view.game_table.blockSignals(False)

    def on_print_clicked(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_coupon(year, week)

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

        coupon = self.model.get_coupon(year, week)

        if coupon is None:
            self.view.update_games([])
            return

        self.view.game_table.blockSignals(True)
        self.view.update_games(coupon.games)
        self.view.game_table.blockSignals(False)
