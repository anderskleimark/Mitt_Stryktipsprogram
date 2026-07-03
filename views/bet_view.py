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

    def create_bet_table(self):

        self.bet_table = QTableWidget()
        self.register_selection_table(self.bet_table)

        self.bet_table.setColumnCount(6)
        self.bet_table.setHorizontalHeaderLabels([
            "Id",
            "Kupong",
            "System",
            "Datum",
            "Antal rätt",
            "Vinst"
        ])

        header = self.bet_table.horizontalHeader()

        # Id
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        # Kupong-id
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        # Systemnamn får ta mest plats
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        # Datum
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        # Antal rätt
        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        # Vinst
        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.bet_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.bet_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.bet_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.bet_table.setAlternatingRowColors(True)

    def create_detail_view(self):

        self.detail_widget = QWidget()
        layout = QVBoxLayout()

        self.detail_table = QTableWidget()

        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels([
            "Hemmalag",
            "Bortalag",
            "Ram",
            "U-tecken"

        ])

        header = self.detail_table.horizontalHeader()
        header.setMinimumSectionSize(80)
        # Hemmalag
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )
        # Bortalag
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout.addWidget(self.detail_table)
        self.detail_widget.setLayout(layout)

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

    def set_buttons_enabled(self, status):
        self.delete_button.setEnabled(status)
        self.show_details_button.setEnabled(status)

    def update_bets(self, bets):

        self.bet_table.clearContents()
        self.bet_table.setRowCount(len(bets))

        for row, bet in enumerate(bets):

            self.bet_table.setItem(
                row,
                0,
                QTableWidgetItem(str(bet.id))
            )

            self.bet_table.setItem(
                row,
                1,
                QTableWidgetItem(str(bet.coupon_id))
            )

            self.bet_table.setItem(
                row,
                2,
                QTableWidgetItem(str(bet.system.display_name))
            )

            self.bet_table.setItem(
                row,
                3,
                QTableWidgetItem(bet.date)
            )

            self.bet_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    "" if bet.correct is None else str(bet.correct))
            )

            self.bet_table.setItem(
                row,
                5,
                QTableWidgetItem("" if bet.prize is None else str(bet.prize))
            )

    def show_table(self):

        self.stacked_widget.setCurrentWidget(
            self.bet_table
        )

        self.show_details_button.setText(
            "Visa detaljer"
        )

    def show_details(self):

        self.stacked_widget.setCurrentWidget(
            self.detail_widget
        )

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

    def update_header_text(self, text):
        self.header.setText(text)

    def update_button_text(self, text):
        self.show_details_button.setText(text)
