from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHeaderView, QLabel, QTableWidget,
                               QTableWidgetItem)

from widgets.base_widget import BaseWidget


class OddsAnalysisWidget(BaseWidget):
    """
        Widget för att visa oddsanalys.

        Visar modellens sannolikheter,
        rättvisa odds och lägsta spelbara
        odds för olika spelmarknader.
    """

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    LABEL_ODDS = "Oddsanalys"

    HEADERS = (
        "Spel",
        "Sannolikhet",
        "Rättvist odds",
        "Spelbart från"
    )

    # --------------------------------------------------
    # Kolumner
    # --------------------------------------------------

    COLUMN_BET = 0
    COLUMN_PROBABILITY = 1
    COLUMN_FAIR_ODDS = 2
    COLUMN_MINIMUM_ODDS = 3

    COLUMN_COUNT = 4

    # --------------------------------------------------
    # Initiering
    # --------------------------------------------------

    def __init__(self):
        """
            Initierar oddsanalyswidgeten.
        """
        super().__init__()

        self.create_widgets()
        self.create_layout()

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar widgetens innehåll.
        """
        self.odds_label = QLabel(self.LABEL_ODDS)
        self.odds_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.odds_table = QTableWidget()
        self.odds_table.setColumnCount(
            self.COLUMN_COUNT
        )
        self.odds_table.setHorizontalHeaderLabels(
            self.HEADERS
        )

        self.odds_table.verticalHeader().setVisible(False)

        header = self.odds_table.horizontalHeader()

        header.setSectionResizeMode(
            self.COLUMN_BET,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            self.COLUMN_PROBABILITY,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            self.COLUMN_FAIR_ODDS,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            self.COLUMN_MINIMUM_ODDS,
            QHeaderView.ResizeMode.ResizeToContents
        )

    def create_layout(self):
        """
            Skapar widgetens layout.
        """
        layout = self.create_vertical_layout(
            parent=self,
            spacing=None
        )

        layout.addWidget(self.odds_label)
        layout.addWidget(self.odds_table)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar oddsanalysen för samtliga
            spelmarknader.
        """
        self.clear_analysis()

        odds_analysis = analysis.odds_analysis

        # 1X2
        self._add_bet_row(
            "1",
            odds_analysis.match_result["1"]
        )

        self._add_bet_row(
            "X",
            odds_analysis.match_result["X"]
        )

        self._add_bet_row(
            "2",
            odds_analysis.match_result["2"]
        )

        # Dubbelchans
        self._add_bet_row(
            "1X",
            odds_analysis.double_chance["1X"]
        )

        self._add_bet_row(
            "12",
            odds_analysis.double_chance["12"]
        )

        self._add_bet_row(
            "X2",
            odds_analysis.double_chance["X2"]
        )

        # Över / under
        for line in (
            1.5,
            2.5,
            3.5,
            4.5
        ):
            bets = odds_analysis.over_under[line]

            self._add_bet_row(
                f"Över {line:.1f}",
                bets["over"]
            )

            self._add_bet_row(
                f"Under {line:.1f}",
                bets["under"]
            )

        # BTTS
        self._add_bet_row(
            "BTTS Ja",
            odds_analysis.btts["yes"]
        )

        self._add_bet_row(
            "BTTS Nej",
            odds_analysis.btts["no"]
        )

    def _add_bet_row(
        self,
        name,
        bet_analysis
    ):
        """
            Lägger till ett spelalternativ
            i oddsanalystabellen.
        """
        row = self.odds_table.rowCount()
        self.odds_table.insertRow(row)

        name_item = QTableWidgetItem(name)

        probability_item = QTableWidgetItem(
            f"{bet_analysis.probability:.1%}"
        )

        fair_odds_item = QTableWidgetItem(
            f"{bet_analysis.fair_odds:.2f}"
        )

        minimum_odds_item = QTableWidgetItem(
            f"{bet_analysis.minimum_odds:.2f}"
        )

        probability_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        fair_odds_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        minimum_odds_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.odds_table.setItem(
            row,
            self.COLUMN_BET,
            name_item
        )

        self.odds_table.setItem(
            row,
            self.COLUMN_PROBABILITY,
            probability_item
        )

        self.odds_table.setItem(
            row,
            self.COLUMN_FAIR_ODDS,
            fair_odds_item
        )

        self.odds_table.setItem(
            row,
            self.COLUMN_MINIMUM_ODDS,
            minimum_odds_item
        )

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_analysis(self):
        """
            Tömmer tidigare oddsanalys.
        """
        self.odds_table.setRowCount(0)
