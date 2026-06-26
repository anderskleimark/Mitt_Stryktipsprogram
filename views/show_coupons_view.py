from mvc import View
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton
)
from PySide6.QtCore import Qt

# Klass som har till uppgift att hantera vyn för att visa tillagda tipskuponger.


class ShowCouponsView(View):

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.setLayout(self.layout)

        self.layout.addWidget(
            self.create_header("Kuponger")
        )

        self.layout.addSpacing(25)

        # Year/Week widget (UI-komponent)
        self.year_week_widget = YearWeekWidget()
        self.layout.addWidget(self.year_week_widget)

        self.create_table()
        self.create_bottom_widget()

    # Funktion för att skapa tabellen med matcherna.
    def create_table(self):

        self.matches_table = QTableWidget(13, 3)

        self.matches_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag", "Resultat"]
        )

        self.matches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        for row in range(13):
            self.matches_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        self.layout.addWidget(self.matches_table)

    # Funktion som skapar widgeten med utskriftsknappen med mera.
    def create_bottom_widget(self):
        bottom_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(0)

        # Knappar
        self.print_button = QPushButton("Skriv ut")
        layout.addWidget(self.print_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion som uppdaterar vyn med den valda kupongen och dess matcher.
    def update_matches(self, matches):
        for row in range(13):
            if row < len(matches):
                match_number, home, away = matches[row]
                result = ""  # inget resultat ännu
            else:
                match_number, home, away, result = "", "", "", ""

            self.matches_table.setItem(row, 0, QTableWidgetItem(home))
            self.matches_table.setItem(row, 1, QTableWidgetItem(away))
            self.matches_table.setItem(row, 2, QTableWidgetItem(result))

    # Funktion som rensar.
    def clear(self):
        for row in range(13):
            for col in range(3):
                self.matches_table.setItem(row, col, QTableWidgetItem(""))
