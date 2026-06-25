from mvc import View
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem
)
from PySide6.QtCore import Qt


class ShowCouponsView(View):

    def __init__(self):
        super().__init__()

        layout = self.create_layout()

        layout.addWidget(
            self.create_header("Kuponger")
        )

        layout.addSpacing(25)

        # Year/Week widget (UI-komponent)
        self.year_week_widget = YearWeekWidget()
        layout.addWidget(self.year_week_widget)

        # Tabell
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

        layout.addWidget(self.matches_table)
        self.setLayout(layout)

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

    def clear(self):
        for row in range(13):
            for col in range(3):
                self.matches_table.setItem(row, col, QTableWidgetItem(""))
