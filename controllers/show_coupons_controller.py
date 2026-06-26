from PySide6.QtWidgets import QMessageBox
from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

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

    def on_year_week_changed(self, year, week):
        self.load_coupon()

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
        <b>Vecka:</b> {coupon.week}
        </p>

        <table border="1"
            cellspacing="0"
            cellpadding="5"
            width="100%">

            <tr>
                <th>Nr</th>
                <th>Hemmalag</th>
                <th>Bortalag</th>
                <th>Resultat</th>
            </tr>
        """

        for match in coupon.matches:

            # Anpassa beroende på hur du lagrar matcherna
            number, home, away = match

            html += f"""
            <tr>
                <td>{number}</td>
                <td>{home}</td>
                <td>{away}</td>
                <td></td>
            </tr>
            """

        html += "</table>"

        return html

    # Funktion för att ladda en tipskupong utifrån vad som har valts i vyn.
    def load_coupon(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_coupon(year, week)

        self.model.current_coupon = coupon

        if coupon is None:
            self.view.update_matches([])
            return

        self.view.update_matches(coupon.matches)
