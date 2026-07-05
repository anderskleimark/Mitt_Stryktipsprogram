from mvc import View
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton,
    QStackedWidget,
    QGridLayout,
    QLineEdit,
    QSpinBox
)
from PySide6.QtCore import Qt
from misc.base_table_widget import BaseTableWidget
from PySide6.QtGui import QIntValidator


# Klass (vy) som visar alla tillagda vad.


class BetView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Vad")
        self.layout.addWidget(self.header)

        # Innehållsväxling mellan tabell och detaljvy
        self.stacked_widget = QStackedWidget()
        self.create_bet_table()
        self.create_detail_view()

        self.stacked_widget.addWidget(self.bet_table)
        self.stacked_widget.addWidget(self.detail_widget)
        self.layout.addWidget(self.stacked_widget)

        # Knappar längst ned
        self.create_bottom_widget()
        self.setLayout(self.layout)

        self.show_table()

    # Funktion som skapar tabellen med de tidigare vaden.
    def create_bet_table(self):

        self.bet_table = BaseTableWidget(True, True, 0, 6)
        self.bet_table.setHorizontalHeaderLabels([
            "Id",
            "Kupong",
            "System",
            "Datum",
            "Antal rätt",
            "Vinst"
        ])

        self.bet_table.set_narrow_columns([0, 1, 3, 4, 5])
        self.bet_table.set_wide_column(2)

    # Funktion som skapar den QWidget med detaljer om ett valt vad.

    def create_detail_view(self):

        self.detail_widget = QWidget()
        layout = QVBoxLayout()

        # Överst visas detaljer i form av datum, system med mera.
        top_widget = QWidget()
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(5)

        self.bet_id_edit = QLineEdit()
        self.bet_id_edit.setReadOnly(True)

        self.date_edit = QLineEdit()
        self.date_edit.setReadOnly(True)

        self.system_edit = QLineEdit()
        self.system_edit.setReadOnly(True)

        self.correct_edit = QSpinBox()
        self.correct_edit.setRange(0, 13)
        self.prize_edit = QSpinBox()
        self.prize_edit.setRange(0, 10_000_000)

        # Rad 1
        grid.addWidget(QLabel("Id:"), 0, 0)
        grid.addWidget(self.bet_id_edit, 0, 1)

        grid.addWidget(QLabel("Datum:"), 0, 2)
        grid.addWidget(self.date_edit, 0, 3)

        grid.addWidget(QLabel("System:"), 0, 4)
        grid.addWidget(self.system_edit, 0, 5)

        # Rad 2
        grid.addWidget(QLabel("Antal rätt:"), 1, 0)
        grid.addWidget(self.correct_edit, 1, 1)

        grid.addWidget(QLabel("Vinst:"), 1, 2)
        grid.addWidget(self.prize_edit, 1, 3)

        top_widget.setLayout(grid)
        layout.addWidget(top_widget)

        self.detail_table = BaseTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels([
            "Hemmalag",
            "Bortalag",
            "Ram",
            "U-tecken"

        ])

        self.detail_table.set_minimum_column_width(80)
        self.detail_table.set_wide_columns([0, 1])
        self.detail_table.set_narrow_columns([2, 3])

        layout.addWidget(self.detail_table)
        self.detail_widget.setLayout(layout)

    # Funktion som skapar den QWidget, som finns längst ned. Den innehåller flera knappar med val.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar

        self.add_bet_button = QPushButton("Lägg till")
        layout.addWidget(self.add_bet_button)

        self.show_details_button = QPushButton("Visa detaljer")
        layout.addWidget(self.show_details_button)

        self.show_table_button = QPushButton("Visa tabell")
        layout.addWidget(self.show_table_button)

        self.delete_button = QPushButton("Radera")
        self.delete_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_button)

        self.set_buttons_enabled(False)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion för att aktivera/deaktivera knappar.
    def set_buttons_enabled(self, status):
        self.delete_button.setEnabled(status)
        self.show_details_button.setEnabled(status)

    # Funktion för att uppdatera tabellen med vad.
    def update_bets(self, bets):

        self.bet_table.clearContents()
        self.bet_table.setRowCount(len(bets))

        for row, bet in enumerate(bets):

            self.bet_table.setItem(row, 0, QTableWidgetItem(str(bet.id)))
            self.bet_table.setItem(
                row, 1, QTableWidgetItem(str(bet.coupon_id)))
            self.bet_table.setItem(row, 2, QTableWidgetItem(
                str(bet.system.display_name)))

            self.bet_table.setItem(row, 3, QTableWidgetItem(bet.date))
            self.bet_table.setItem(row, 4, QTableWidgetItem(
                "" if bet.correct is None else str(bet.correct)))
            self.bet_table.setItem(row, 5, QTableWidgetItem(
                "" if bet.prize is None else str(bet.prize)))

    # Funktion för att visa tabellen med de olika vaden.
    def show_table(self):

        self.header.show()
        self.show_details_button.show()
        self.show_table_button.hide()
        self.stacked_widget.setCurrentWidget(self.bet_table)

    # Funktion för att visa vyn med detaljer om ett valt vad.
    def show_details(self):

        self.header.hide()
        self.show_details_button.hide()
        self.show_table_button.show()
        self.stacked_widget.setCurrentWidget(self.detail_widget)

    # Funktion som uppdaterar detaljerna om det valda vadet.
    def update_bet_info(self, bet):

        self.bet_id_edit.setText(str(bet.id))
        self.date_edit.setText(bet.date)
        self.system_edit.setText(bet.system.display_name)

        # Blockera signaler så att autosparning inte triggas
        self.correct_edit.blockSignals(True)
        self.prize_edit.blockSignals(True)

        self.correct_edit.setValue(0 if bet.correct is None else bet.correct)
        self.prize_edit.setValue(0 if bet.prize is None else bet.prize)

        self.correct_edit.blockSignals(False)
        self.prize_edit.blockSignals(False)

    # Funktion för att uppdatera tabellen med detaljer.
    def update_detail_table(self, games):

        self.detail_table.clearContents()
        self.detail_table.setRowCount(len(games))

        for row, game in enumerate(games):

            self.detail_table.setItem(row, 0, QTableWidgetItem(game.home_team))

            self.detail_table.setItem(row, 1, QTableWidgetItem(game.away_team))

            self.detail_table.setItem(row, 2, QTableWidgetItem(""))

            self.detail_table.setItem(row, 3, QTableWidgetItem(""))

    # Funktion som visar/döljer kolumnen med U-tecken.abs
    def show_key_row_column(self, visible=True):
        self.detail_table.setColumnHidden(3, not visible)

    # Funktion som ändrar texten på en knapp.
    def update_button_text(self, text):
        self.show_details_button.setText(text)

    # Superfunktion, som behövs för att rensa markering, om man klickar utanför tabellen.
    def get_active_selection_table(self):

        if self.stacked_widget.currentWidget() == self.bet_table:
            return self.bet_table

        return self.detail_table

    # Funktion som rensar detaljinformation om ett visst vad.
    def clear_bet_info(self):

        self.bet_id_edit.clear()
        self.date_edit.clear()
        self.system_edit.clear()

        self.correct_edit.blockSignals(True)
        self.prize_edit.blockSignals(True)

        self.correct_edit.setValue(0)
        self.prize_edit.setValue(0)

        self.correct_edit.blockSignals(False)
        self.prize_edit.blockSignals(False)
