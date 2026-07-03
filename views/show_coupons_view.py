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

        self.create_header("Kuponger")
        self.layout.addWidget(self.header)

        self.layout.addSpacing(25)

        # Year/Week widget (UI-komponent)
        self.year_week_widget = YearWeekWidget()
        self.layout.addWidget(self.year_week_widget)

        self.create_table()
        self.create_bottom_widget()

    def get_active_selection_table(self):
        return self.game_table

    # Funktion för att skapa tabellen med matcherna.
    def create_table(self):

        self.game_table = QTableWidget(13, 5)
        # self.register_selection_table(self.game_table)
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
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.print_button = QPushButton("Skriv ut")
        self.print_button.setEnabled(False)
        layout.addWidget(self.print_button)
        self.delete_button = QPushButton("Radera")
        self.delete_button.setEnabled(False)
        self.delete_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_button)

        # Layout
        bottom_widget.setLayout(layout)
        self.layout.addWidget(bottom_widget)

    # Funktion som uppdaterar vyn med den valda kupongen och dess matcher.
    def update_games(self, games):

        self.game_table.blockSignals(True)

        self.game_table.clearContents()
        self.game_table.setRowCount(len(games))

        for row, game in enumerate(games):

            self.game_table.setItem(row, 0, QTableWidgetItem(game.home_team))
            self.game_table.setItem(row, 1, QTableWidgetItem(game.away_team))

            self.game_table.setItem(
                row, 2,
                QTableWidgetItem(
                    "" if game.home_score is None else str(game.home_score))
            )

            self.game_table.setItem(
                row, 3,
                QTableWidgetItem(
                    "" if game.away_score is None else str(game.away_score))
            )

            # ⭐ 1X2
            self.game_table.setItem(
                row, 4,
                QTableWidgetItem(game.result_1x2)
            )

        self.game_table.blockSignals(False)

    # Funktion som aktiverar eller deaktiverar knapparna.
    def set_buttons_enabled(self, enabled):
        self.print_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    # Funktion som rensar.

    def clear(self):
        for row in range(13):
            for col in range(3):
                self.game_table.setItem(row, col, QTableWidgetItem(""))
