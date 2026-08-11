from collections import Counter

from misc.system_validator import SystemValidator
from mvc import Controller


class BetController(Controller):
    """
        Klass som hanterar vad, system, detaljer och statistik.
    """

    def __init__(
        self, *,
        bet_model,
        coupon_model,
        system_model,
        view
    ):
        super().__init__(view)
        self.bet_model = bet_model
        self.coupon_model = coupon_model
        self.system_model = system_model
        self.validator = SystemValidator()
        self.add_connections()
        self.current_bet = None
        self.load_bets()

    def add_connections(self):
        """
            Kopplar signaler till slots.
        """
        self.view.add_bet_button.clicked.connect(
            self.on_add_bet_clicked
        )

        self.view.delete_bet_button.clicked.connect(
            self.on_delete_bet_button_clicked
        )

        self.view.bet_selection_changed.connect(
            self.on_bet_selection_changed
        )

        self.view.show_details_button.clicked.connect(
            self.on_show_details_clicked
        )

        self.view.show_overview_button.clicked.connect(
            self.on_show_overview_clicked
        )

        self.view.bet_result_changed.connect(
            self.on_auto_save
        )

        self.view.open_graph_button.clicked.connect(
            self.on_open_graph_button_clicked
        )

        self.view.back_from_graph_widget_button.clicked.connect(
            self.on_back_from_graph_widget_button_clicked
        )

        self.view.copy_diagram_button.clicked.connect(
            self.on_copy_diagram_button_clicked
        )

        self.view.save_diagram_as_image_button.clicked.connect(
            self.on_save_diagram_as_image_button_clicked
        )

        self.view.frame_changed.connect(
            self.on_frame_changed
        )

        self.view.key_changed.connect(
            self.on_key_changed
        )

        self.view.math_changed.connect(
            self.on_math_changed
        )

    def load_bets(self):
        """
            Hämtar alla vad.
        """
        # Hämtar alla vad från databasen.
        self.bets = self.bet_model.get_all()

        # Rensa tidigare data.
        self.current_bet = None
        self.view.set_buttons_enabled(False)

        # Uppdatera översiktstabellen.
        self.view.update_overview_table(self.bets)

    def on_add_bet_clicked(self):
        """
            Lägger till ett nytt vad.
        """
        result = self.view.show_add_bet_dialog(
            coupons=self.coupon_model.get_all(),
            systems=self.system_model.get_all()
        )

        if result is None:
            return

        coupon_id, system_id, date = result

        try:
            self.bet_model.add_bet(
                coupon_id, system_id, date
            )
            self.load_bets()

        except ValueError as error:
            self.view.show_warning(
                "Fel",
                str(error)
            )

    def on_delete_bet_button_clicked(self):
        """
            Raderar valt vad.
        """
        if self.current_bet is None:
            return
        if not self.view.ask_confirmation(
            "Radera vad",
            "Är du säker på att du vill radera vadet?"
        ):
            return

        self.bet_model.delete(self.current_bet.id)
        self.load_bets()

        # Rensning.
        self.view.clear_bet_info()

    def on_show_details_clicked(self):
        """
            Visar detaljer för valt vad.
        """
        if self.current_bet is None:
            return

        # Ställ in vilket tipssystem som används.
        self.validator.set_system(self.current_bet.system)

        if self.current_bet.system.system_type in ("R", "M"):
            self.view.show_key_row_column(False)
        else:
            self.view.show_key_row_column(True)

        # Uppdatera totalkostnaden för vadet.
        self.update_total_cost()

        # Uppdatera validatorerna.
        details = self.bet_model.get_bet_details(self.current_bet.id)
        self.update_validator_from_details(details)

        # Skicka validatorn till vyn
        coupon = self.coupon_model.get(self.current_bet.coupon.id)
        self.view.update_detail_table(
            coupon.soccer_matches,
            details,
            self.validator
        )

        # Visa statistik över hel/halv/givna
        self.view.update_system_statistics(
            self.validator.get_statistics())

        self.view.update_bet_info(self.current_bet)
        self.view.show_details()

    def on_show_overview_clicked(self):
        """
            Visar översikten.
        """
        self.current_bet = None
        self.view.clear_bet_info()
        self.view.show_overview()

    def on_open_graph_button_clicked(self):
        """
            Öppnar statistikgrafen.
        """
        data, average = self.build_graph_data()
        self.view.update_statistic_graph(data, average)
        self.view.show_graph_widget()

    def on_back_from_graph_widget_button_clicked(self):
        """
            Går tillbaka från grafvyn.
        """
        self.view.show_overview()

    def on_copy_diagram_button_clicked(self):
        """
            Kopierar diagram till urklipp.
        """
        self.view.copy_diagram_to_clipboard()

    def on_save_diagram_as_image_button_clicked(self):
        """
            Sparar diagram som bild.
        """
        self.view.save_diagram_as_image()

    def on_bet_selection_changed(self):
        """
            Hanterar ändrad markering av vad.
        """
        row = self.view.get_selected_bet_row()
        if row >= 0:
            self.current_bet = self.bets[row]
            self.view.update_bet_info(self.current_bet)
        else:
            self.current_bet = None
            self.view.clear_bet_info()

        self.view.set_buttons_enabled(row >= 0)

    def on_auto_save(self):
        """
            Sparar ändrade resultat automatiskt.
        """
        if self.current_bet is None:
            return

        correct_count, prize = self.view.get_bet_result()

        if (
            correct_count == self.current_bet.correct_count
            and prize == self.current_bet.prize
        ):
            return

        self.bet_model.update_bet_result(
            self.current_bet.id,
            correct_count,
            prize
        )

        self.current_bet.correct_count = correct_count
        self.current_bet.prize = prize

        row = self.view.get_selected_bet_row()

        if row >= 0:
            self.view.update_bet_result_row(
                row,
                correct_count,
                prize
            )

    def on_frame_changed(self, match_number, frame):
        """
            Sparar ändrat ramsystem.
        """
        if not self.is_valid_match(match_number):
            return

        self.bet_model.save_detail(
            self.current_bet.id,
            match_number,
            frame=frame
        )

        # Uppdatera ram-validatorn
        self.validator.set_frame_value(match_number, frame)

        # Uppdatera statistik-korten
        self.view.update_system_statistics(
            self.validator.get_statistics())

        # Uppdatera ram-comboboxar
        self.view.refresh_frame_combos(self.validator)

        # Uppdatera U-tecken-comboboxar
        self.view.refresh_key_combos(self.validator)

    def on_key_changed(self, match_number, key):
        """
            Sparar ändrat U-tecken.
        """
        if not self.is_valid_match(match_number):
            return

        self.bet_model.save_key(
            self.current_bet.id,
            match_number,
            key
        )

        self.validator.set_key_value(match_number, key)

    def on_math_changed(self, match_number, checked):
        """
            Sparar ändrad matematisk markering.
        """
        if not self.is_valid_match(match_number):
            return

        self.bet_model.save_mathematical_value(
            self.current_bet.id,
            match_number,
            checked
        )

        self.validator.set_mathematical_value(match_number, checked)

        # Om matchen blir matematisk: ta bort U-tecken
        if checked:
            self.bet_model.save_key(
                self.current_bet.id,
                match_number,
                ""
            )
            self.validator.set_key_value(match_number, "")

        # Uppdatera den totala kostnaden för vadet.
        self.update_total_cost()
        self.view.update_bet_info(self.current_bet)

        self.view.update_system_statistics(
            self.validator.get_statistics())

        # Uppdatera U-tecken-comboboxarna
        self.view.refresh_key_combos(self.validator)

    def build_graph_data(self):
        """
            Skapar data till statistikgrafen.
        """
        values = [bet.correct_count
                  for bet in self.bets
                  if bet.correct_count is not None]

        counter = Counter(values)

        # Medelvärde.
        average = (
            sum(values) / len(values)
            if values
            else 0
        )

        data = [
            {"ratt": i, "antal": counter.get(i, 0)}
            for i in range(0, 14)   # 0–13
        ]

        return data, average

    def update_total_cost(self):
        """
            Uppdaterar kostnaden för vadet.
        """
        if self.current_bet is None:
            return

        factor = self.bet_model.get_price_factor(self.current_bet.id)

        self.current_bet.total_cost = (
            self.current_bet.system.row_count * factor
        )

    def update_validator_from_details(self, details):
        """
            Uppdaterar validatorn med vadets detaljer.
        """
        count = self.validator.MATCH_COUNT

        frame_values = [""] * count
        key_values = [""] * count
        math_values = [False] * count

        for detail in details:
            index = detail.match_number - 1

            frame_values[index] = detail.frame_value
            key_values[index] = detail.key_value or ""
            math_values[index] = detail.mathematical_value

        self.validator.update_frame_values(frame_values)
        self.validator.update_mathematical_values(math_values)
        self.validator.update_key_values(key_values)

    def is_valid_match(self, match_number):
        """
            Kontrollerar om matchnumret är giltigt.
        """
        return self.current_bet is not None and (
            1 <= match_number <= self.validator.MATCH_COUNT
        )
