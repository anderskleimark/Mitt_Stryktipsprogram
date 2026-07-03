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
    QStackedWidget
)
from PySide6.QtCore import Qt
from misc.base_table_widget import BaseTableWidget

# Klass (vy) som visar alla tillagda vad.


class BetView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Historik")
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

        self.stacked_widget.setCurrentWidget(
            self.bet_table
        )

        self.show_details_button.setText(
            "Visa detaljer"
        )

    # Funktion för att visa vyn med detaljer om ett valt vad.
    def show_details(self):

        self.stacked_widget.setCurrentWidget(
            self.detail_widget
        )

    # Funktion för att uppdatera tabellen med detaljer.
    def update_detail_table(self, games):

        self.detail_table.clearContents()
        self.detail_table.setRowCount(len(games))

        for row, game in enumerate(games):

            self.detail_table.setItem(
                row,
                0,
                QTableWidgetItem(game.home_team)
            )

            self.detail_table.setItem(
                row,
                1,
                QTableWidgetItem(game.away_team)
            )

            self.detail_table.setItem(
                row,
                2,
                QTableWidgetItem("")

            )

            self.detail_table.setItem(
                row,
                3,
                QTableWidgetItem("")

            )
    # Funktion som visar/döljer kolumnen med U-tecken.abs

    def show_key_row_column(self, visible=True):
        self.detail_table.setColumnHidden(3, not visible)

    # Funktion som ändrar rubriktexten.
    def update_header_text(self, text):
        self.header.setText(text)

    # Funktion som ändrar texten på en knapp.
    def update_button_text(self, text):
        self.show_details_button.setText(text)

    # Superfunktion, som behövs för att rensa markering, om man klickar utanför tabellen.
    def get_active_selection_table(self):

        if self.stacked_widget.currentWidget() == self.bet_table:
            return self.bet_table

        return self.detail_table
