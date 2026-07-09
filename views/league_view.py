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
    QSpinBox,
    QFrame,
    QFileDialog
)
from misc.base_table_widget import BaseTableWidget

# Klass (View) som visar information om lag, tabeller med mera.


class LeagueView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Ligor")
        self.layout.addWidget(self.header)
        self.create_league_table()

        self.create_bottom_widget()
        self.setLayout(self.layout)

    # Funktion som skapar tabellen med ligor.
    def create_league_table(self):
        self.league_table = BaseTableWidget(True, True, 0, 3)
        self.league_table.setHorizontalHeaderLabels([
            "Id",
            "Land",
            "Namn"
        ])

        self.layout.addWidget(self.league_table)

    # Funktion som skapar den undre widgeten med olika knappar.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.add_league_button = QPushButton("Lägg till")
        layout.addWidget(self.add_league_button)

        self.delete_league_button = QPushButton("Radera")
        self.delete_league_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_league_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion som körs, när tabellen uppdateras.
    def update_league_table(self, leagues):

        self.league_table.clearContents()
        self.league_table.setRowCount(len(leagues))

        for row, league in enumerate(leagues):

            self.league_table.setItem(
                row, 0, QTableWidgetItem(str(league.id))
            )

            self.league_table.setItem(
                row, 1, QTableWidgetItem(league.name)
            )

            self.league_table.setItem(
                row, 2, QTableWidgetItem(league.country)
            )

            self.league_table.set_narrow_columns([0, 1])
            self.league_table.set_wide_column(2)

    def get_active_selection_table(self):
        return self.league_table
