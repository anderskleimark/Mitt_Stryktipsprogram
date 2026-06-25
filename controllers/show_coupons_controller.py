from PySide6.QtWidgets import QMessageBox
from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget


class ShowCouponsController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()

    def add_connections(self):
        self.view.year_week_widget.year_week_changed.connect(
            self.on_year_week_changed
        )

    def on_year_week_changed(self, year, week):
        self.load_coupon()

    # Funktion för att ladda en tipskupong utifrån vad som har valts i vyn.
    def load_coupon(self):
        year = self.view.year_week_widget.get_year()
        week = self.view.year_week_widget.get_week()

        coupon = self.model.get_coupon(year, week)

        if coupon is None:
            self.view.update_matches([])  # tom tabell
            return

        self.view.update_matches(coupon.matches)
