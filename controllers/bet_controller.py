from collections import Counter
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from misc.create_bet_dialog import CreateBetDialog
from misc.system_validator import SystemValidator
from mvc import Controller

# Klass (Controller), som samarbetar med vyn, som visar information om olika vad.


class BetController(Controller):

    def __init__(self, bet_model, coupon_model, system_model, view):
        super().__init__(bet_model, view)
        self.coupon_model = coupon_model
        self.system_model = system_model
        self.validator = SystemValidator()
        self.add_connections()
        self.current_bet = None
        self.load_bets()

    def add_connections(self):
        self.view.add_bet_button.clicked.connect(self.on_create_bet_clicked)
        self.view.delete_bet_button.clicked.connect(
            self.on_delete_bet_button_clicked)

        self.view.bet_table.itemSelectionChanged.connect(
            self.on_selection_changed)
        self.view.show_details_button.clicked.connect(
            self.on_show_details_clicked)
        self.view.show_overview_button.clicked.connect(
            self.on_show_overview_clicked)
        self.view.correct_edit.valueChanged.connect(self.on_auto_save)
        self.view.prize_edit.valueChanged.connect(self.on_auto_save)
        self.view.open_graph_button.clicked.connect(
            self.on_open_graph_button_clicked)
        self.view.back_from_graph_widget_button.clicked.connect(
            self.on_back_from_graph_widget_button_clicked)
        self.view.copy_diagram_button.clicked.connect(
            self.on_copy_diagram_button_clicked)
        self.view.save_diagram_as_image_button.clicked.connect(
            self.on_save_diagram_as_image_button_clicked)
        self.view.frame_changed.connect(self.on_frame_changed)
        self.view.key_changed.connect(self.on_key_changed)
        self.view.math_changed.connect(self.on_math_changed)

    # Funktion som hämtar information om alla vad.
    def load_bets(self):
        self.bets = self.model.get_all()

        # Rensa tidigare data.
        self.current_bet = None
        self.view.set_buttons_enabled(False)

        self.view.update_overview_table(self.bets)

    # Funktion som triggas, när användaren klickar på "Lägg till".
    def on_create_bet_clicked(self):
        dialog = CreateBetDialog(
            self.coupon_model.get_all(), self.system_model.get_all(), self.view)

        if dialog.exec():
            self.model.create_bet(
                dialog.coupon_id, dialog.system_id, dialog.date)
            self.load_bets()

    # Funktion som triggas, när användaren vill radera ett vad.
    def on_delete_bet_button_clicked(self):
        if self.current_bet is None:
            return
        reply = QMessageBox.question(
            self.view,
            "Radera vad",
            "Är du säker på att du vill radera vadet?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        bet_id = self.current_bet.id
        self.model.delete(bet_id)
        self.load_bets()

        # Rensning.
        self.view.clear_bet_info()

    # Funktion som triggas, när användaren klickar på "Visa detaljer".
    def on_show_details_clicked(self):
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
        details = self.model.get_bet_details(self.current_bet.id)
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
            self.validator.get_statistics()
        )

        self.view.update_bet_info(self.current_bet)
        self.view.show_details()

    # Funktion som triggas, när användaren klickar på "Visa tabell".
    def on_show_overview_clicked(self):
        self.current_bet = None
        self.view.clear_bet_info()
        self.view.show_overview()

    # Funktion som triggas, när användaren väljer att klicka på "Öppna graf"
    def on_open_graph_button_clicked(self):
        data, average = self.build_graph_data()
        self.view.update_statistic_graph(data, average)

        self.view.show_graph_widget()

    # Funktion som triggas, om användaren går tillbaka till översikten.
    def on_back_from_graph_widget_button_clicked(self):
        self.view.show_overview()

    # Funktion som anropar en funktion i vyn för att kopiera diagrammet.
    def on_copy_diagram_button_clicked(self):
        self.view.copy_diagram_to_clipboard()

    # Funktion som anropar en funktion i vyn för att spara diagrammet som en bild.
    def on_save_diagram_as_image_button_clicked(self):
        self.view.save_diagram_as_image()

    # Funktion som triggas, om vald rad ändras.
    def on_selection_changed(self):
        row = self.get_selected_bet_row()

        if row >= 0:
            self.current_bet = self.bets[row]
            self.view.update_bet_info(self.current_bet)

        else:
            self.current_bet = None
            self.view.clear_bet_info()

        self.view.set_buttons_enabled(row >= 0)

    # Funktion som sparar data till databasen, om någonting har ändrats.
    def on_auto_save(self):
        if self.current_bet is None:
            return

        CORRECT_COLUMN = 4
        PRIZE_COLUMN = 5

        correct_count = self.view.correct_edit.value()
        prize = self.view.prize_edit.value()

        # Spara endast om något ändrats
        if (correct_count == self.current_bet.correct_count and
                prize == self.current_bet.prize):
            return

        # Uppdatera databas
        self.model.update_bet_result(
            self.current_bet.id,
            correct_count,
            prize
        )

        # Uppdatera objektet
        self.current_bet.correct_count = correct_count
        self.current_bet.prize = prize

        # Uppdatera endast tabellraden
        row = self.get_selected_bet_row()

        if row >= 0:
            self.view.bet_table.setItem(
                row,
                CORRECT_COLUMN,
                QTableWidgetItem(str(correct_count))
            )

            self.view.bet_table.setItem(
                row,
                PRIZE_COLUMN,
                QTableWidgetItem(str(prize))
            )

    # Funktion som triggas, om ett värde i ramen i någon match ändras.
    def on_frame_changed(self, match_number, frame):
        if not self.is_valid_match(match_number):
            return

        self.model.save_detail(
            self.current_bet.id,
            match_number,
            frame=frame
        )

        # Uppdatera ram-validatorn
        self.validator.set_frame_value(match_number, frame)

        # Uppdatera statistik-korten
        self.view.update_system_statistics(
            self.validator.get_statistics()
        )

        # Uppdatera ram-comboboxar
        self.view.refresh_frame_combos(
            self.validator
        )

        # Uppdatera U-tecken-comboboxar
        self.view.refresh_key_combos(
            self.validator
        )

    # Funktion som triggas när ett U-tecken ändras.
    def on_key_changed(self, match_number, key):
        if not self.is_valid_match(match_number):
            return

        self.model.save_key(
            self.current_bet.id,
            match_number,
            key
        )

        self.validator.set_key_value(match_number, key)

    # Funktion som triggas, när en match ändras beträffande matematisk gardering.
    def on_math_changed(self, match_number, checked):
        if not self.is_valid_match(match_number):
            return

        self.model.save_mathematical(
            self.current_bet.id,
            match_number,
            checked
        )

        self.validator.set_mathematical_value(match_number, checked)

        # Om matchen blir matematisk: ta bort U-tecken
        if checked:
            self.model.save_key(
                self.current_bet.id,
                match_number,
                ""
            )
            self.validator.set_key_value(match_number, "")

        # Uppdatera den totala kostnaden för vadet.
        self.update_total_cost()
        self.view.update_bet_info(self.current_bet)

        self.view.update_system_statistics(
            self.validator.get_statistics()
        )

        # Uppdatera U-tecken-comboboxarna
        self.view.refresh_key_combos(
            self.validator
        )

    # Funktion som returnerar grafens data.
    def build_graph_data(self):
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

    # Funktion för att uppdatera den totala kostnaden för ett vad.
    def update_total_cost(self):
        if self.current_bet is None:
            return

        factor = self.model.get_price_factor(
            self.current_bet.id
        )

        self.current_bet.total_cost = (
            self.current_bet.system.rows * factor
        )

    # Funktion som uppdaterar validatorerna med data från detaljer från vadet.
    def update_validator_from_details(self, details):
        count = self.validator.MATCH_COUNT

        frame_values = [""] * count
        key_values = [""] * count
        math_values = [False] * count

        for detail in details:
            index = detail.match_number - 1

            frame_values[index] = detail.frame_value
            key_values[index] = detail.key_value or ""
            math_values[index] = detail.mathematical

        self.validator.update_frame_values(
            frame_values
        )

        self.validator.update_mathematical_values(
            math_values
        )

        self.validator.update_key_values(
            key_values
        )

    # Funktion som returnerar det aktiva vadets radnummer.
    def get_selected_bet_row(self):
        return self.view.bet_table.currentRow()

    # Funktion som avgör om en match är tillåten eller ej.
    def is_valid_match(self, match_number):
        return self.current_bet is not None and 1 <= match_number <= self.validator.MATCH_COUNT
