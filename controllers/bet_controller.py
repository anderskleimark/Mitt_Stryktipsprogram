from mvc import Controller
from misc.create_bet_dialog import CreateBetDialog
from collections import Counter


class BetController(Controller):

    def __init__(self, bet_model, coupon_model, system_model, view):
        super().__init__(bet_model, view)
        self.coupon_model = coupon_model
        self.system_model = system_model
        self.add_connections()
        self.current_bet = None
        self.load_bets()

    def add_connections(self):
        self.view.add_bet_button.clicked.connect(self.on_create_bet_clicked)
        self.view.bet_table.itemSelectionChanged.connect(
            self.on_selection_changed)
        self.view.show_details_button.clicked.connect(
            self.on_show_details_clicked)
        self.view.show_table_button.clicked.connect(
            self.on_show_table_clicked)
        self.view.correct_edit.valueChanged.connect(self.on_auto_save)
        self.view.prize_edit.valueChanged.connect(self.on_auto_save)
        self.view.open_graph_button.clicked.connect(
            self.on_open_graph_button_clicked)
        self.view.back_from_graph_widget_button.clicked.connect(
            self.on_back_from_graph_widget_button_clicked)

    # Funktion som triggas, när användaren klickar på "Lägg till".
    def on_create_bet_clicked(self):

        dialog = CreateBetDialog(
            self.coupon_model.get_all(), self.system_model.get_all(), self.view)

        if dialog.exec():

            self.model.create_bet(
                dialog.coupon_id, dialog.system_id, dialog.date)
            self.load_bets()

    # Funktion som triggas, när användaren klickar på "Visa detaljer".
    def on_show_details_clicked(self):

        if self.current_bet is None:
            return

        bet = self.current_bet

        if bet.system.system_type in ("R", "M"):
            self.view.show_key_row_column(False)
        else:
            self.view.show_key_row_column(True)

        coupon = self.coupon_model.get(bet.coupon_id)

        self.view.update_detail_table(coupon.games)
        self.view.update_bet_info(bet)
        self.view.show_details()

    # Funktion som triggas, när användaren klickar på "Visa tabell".
    def on_show_table_clicked(self):
        self.current_bet = None
        self.view.clear_bet_info()
        self.view.show_table()

    # Funktion som triggas, när användaren väljer att klicka på "Öppna graf"
    def on_open_graph_button_clicked(self):
        data = self.build_graph_data()
        self.view.update_statistic_graph(data)
        self.view.show_graph_widget()

    # Funktion som triggas, om användaren går tillbaka till översikten.
    def on_back_from_graph_widget_button_clicked(self):
        self.view.show_table()

    # Funktion som hämtar information om alla vad.
    def load_bets(self):
        self.bets = self.model.get_all()

        for bet in self.bets:
            bet.system = self.system_model.get(bet.system_id)

        self.view.update_bets(self.bets)

    # Funktion som returnerar detaljer om ett angivet vad.
    def get_bet_details(self, bet):
        return self.model.get_bet_details(bet.id)

    # Funktion som triggas, om vald rad ändras.
    def on_selection_changed(self):

        row = self.view.bet_table.get_selected_row()

        if row >= 0:
            self.current_bet = self.bets[row]
        else:
            self.current_bet = None

        self.view.set_buttons_enabled(row >= 0)

    # Funktion som sparar data till databasen, om någonting har ändrats.
    def on_auto_save(self):

        if self.current_bet is None:
            return

        correct = self.view.correct_edit.value()
        prize = self.view.prize_edit.value()

        if (correct == self.current_bet.correct and prize == self.current_bet.prize):
            return

        self.current_bet.correct = correct
        self.current_bet.prize = prize
        self.model.update_bet_result(self.current_bet.id, correct, prize)

        self.load_bets()

    # Funktion som returnerar grafens data.
    def build_graph_data(self):
        values = [bet.correct
                  for bet in self.bets
                  if bet.correct is not None]

        counter = Counter(values)

        data = [
            {"ratt": i, "antal": counter.get(i, 0)}
            for i in range(0, 14)   # 0–13
        ]

        return data
