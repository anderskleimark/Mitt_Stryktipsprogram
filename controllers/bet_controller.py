from mvc import Controller
from misc.create_bet_dialog import CreateBetDialog


class BetController(Controller):

    def __init__(self, bet_model, coupon_model, system_model, view):
        super().__init__(bet_model, view)
        self.coupon_model = coupon_model
        self.system_model = system_model
        self.add_connections()
        self.load_bets()

    def add_connections(self):
        self.view.add_bet_button.clicked.connect(self.on_create_bet_clicked)
        self.view.bet_table.itemSelectionChanged.connect(
            self.on_selection_changed)
        self.view.show_details_button.clicked.connect(
            self.on_show_details_clicked)

    def on_create_bet_clicked(self):

        dialog = CreateBetDialog(
            self.coupon_model.get_all(),
            self.system_model.get_all(),
            self.view
        )

        if dialog.exec():

            self.model.create_bet(
                dialog.coupon_id,
                dialog.system_id,
                dialog.date
            )

            self.load_bets()

    def on_show_details_clicked(self):

        if self.view.stacked_widget.currentWidget() == self.view.bet_table:

            row = self.view.bet_table.get_selected_row()
            if row < 0:
                return

            bet = self.bets[row]
            if bet.system.system_type in ("R", "M"):
                self.view.show_key_row_column(False)
            else:
                self.view.show_key_row_column(False)

            coupon = self.coupon_model.get(bet.coupon_id)

            # Rubrik + knapp
            self.view.update_header_text(
                f"Information om vad {bet.id} - {bet.date}"
            )
            self.view.update_button_text("Visa tabell")

            # hämta detaljer
            details = self.load_bet_details(bet)

            self.view.update_detail_table(coupon.games)
            self.view.show_details()

        else:
            self.view.update_header_text("Historik")
            self.view.update_button_text("Visa detaljer")
            self.view.show_table()

    def load_bets(self):
        self.bets = self.model.get_all()

        for bet in self.bets:
            bet.system = self.system_model.get(bet.system_id)

        self.view.update_bets(self.bets)

    def load_bet_details(self, bet):
        return self.model.get_bet_details(bet.id)

    def on_selection_changed(self):

        row = self.view.bet_table.get_selected_row()
        self.view.set_buttons_enabled(row >= 0)
