from mvc import View
from models.coupon_model import Game
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
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStyledItemDelegate, QSpinBox

# Klass för att hantera numeriska kolumner.


class ScoreDelegate(QStyledItemDelegate):
    MIN_VALUE = 0
    MAX_VALUE = 20

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(self.MIN_VALUE, self.MAX_VALUE)
        return editor

    def setEditorData(self, editor, index):
        text = index.data()

        if text == "":
            editor.setValue(0)
        else:
            editor.setValue(int(text))

    def setModelData(self, editor, model, index):
        model.setData(index, str(editor.value()))


# Klass som har till uppgift att hantera vyn för att visa tillagda tipskuponger.

class ShowCouponsView(View):

    # Skickas när användaren ändrar mål
    # row, home_score, away_score
    score_changed = Signal(int, int, int)

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

        self.game_table = QTableWidget(13, 5)

        self.game_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag", "Hemmamål", "Bortamål", "1X2"]
        )

        self.game_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        for row in range(13):
            self.game_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        # Gör målkolumnerna numeriska
        delegate = ScoreDelegate()
        self.game_table.setItemDelegateForColumn(2, delegate)
        self.game_table.setItemDelegateForColumn(3, delegate)

        self.layout.addWidget(self.game_table)

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
    def update_games(self, games):
        self.game_table.blockSignals(True)

        for row in range(13):

            if row < len(games):
                game = games[row]

                home = game.home_team
                away = game.away_team
                home_score = "" if game.home_score is None else str(
                    game.home_score)
                away_score = "" if game.away_score is None else str(
                    game.away_score)
                result = game.result_1x2
            else:
                home = away = home_score = away_score = result = ""

            self.game_table.setItem(row, 0, QTableWidgetItem(home))
            self.game_table.setItem(row, 1, QTableWidgetItem(away))
            self.game_table.setItem(row, 2, QTableWidgetItem(home_score))
            self.game_table.setItem(row, 3, QTableWidgetItem(away_score))

            # Skrivskydd av kolumn fyra.
            result_item = QTableWidgetItem(result)
            result_item.setFlags(
                result_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.game_table.setItem(row, 4, result_item)

        self.game_table.blockSignals(False)

    # Funktion som rensar.

    def clear(self):
        for row in range(13):
            for col in range(3):
                self.game_table.setItem(row, col, QTableWidgetItem(""))
