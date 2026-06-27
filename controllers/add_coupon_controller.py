from PySide6.QtWidgets import QMessageBox
from mvc import Model, View, Controller
from widgets.year_week_widget import YearWeekWidget


class AddCouponController(Controller):
    def __init__(self, model, view):
        super().__init__(model, view)

        self.view.save_button.clicked.connect(self.save_coupon)
        self.view.clear_button.clicked.connect(self.clear_form)

    # Funktion för att spara en tipskupong.
    def save_coupon(self):

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

    # Funktion för att rensa formuläret i vyn.
    def clear_form(self):
        self.view.clear_form()
