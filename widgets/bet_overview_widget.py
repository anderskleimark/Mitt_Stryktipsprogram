from PySide6.QtWidgets import QTableWidgetItem

from misc.base_table_widget import BaseTableWidget
from widgets.base_widget import BaseWidget


class BetOverviewWidget(BaseWidget):
    """
        Widget som visar översikten över sparade vad.
    """

    COLUMN_ID = 0
    COLUMN_COUPON = 1
    COLUMN_SYSTEM = 2
    COLUMN_YEAR_WEEK = 3
    COLUMN_CORRECT = 4
    COLUMN_PRIZE = 5
    COLUMN_COUNT = 6

    TABLE_HEADERS = (
        "Id",
        "Kupong",
        "System",
        "Omgång",
        "Antal rätt",
        "Vinst"
    )

    def __init__(self):
        super().__init__()
        self._build_widget()

    def _build_widget(self):
        """
            Skapar översikten med tabellen över tidigare vad.
        """
        layout = self.create_vertical_layout(
            parent=self,
            spacing=None
        )

        self.bet_table = BaseTableWidget(
            readonly=True,
            rowselection=True,
            cols=self.COLUMN_COUNT
        )

        self.bet_table.setHorizontalHeaderLabels(self.TABLE_HEADERS)

        self.bet_table.set_narrow_columns([
            self.COLUMN_ID,
            self.COLUMN_COUPON,
            self.COLUMN_YEAR_WEEK,
            self.COLUMN_CORRECT,
            self.COLUMN_PRIZE
        ])

        self.bet_table.set_wide_column(self.COLUMN_SYSTEM)
        layout.addWidget(self.bet_table)

    def update_widget(
        self,
        bets
    ):
        """
            Uppdaterar tabellen med tidigare vad.
        """
        self.bet_table.clearContents()
        self.bet_table.setRowCount(len(bets))

        for row, bet in enumerate(bets):
            values = (
                bet.id,
                bet.coupon.id,
                bet.system.display_name,
                (
                    f"{bet.coupon.coupon_year} "
                    f"v.{bet.coupon.coupon_week}"
                ),
                (
                    ""
                    if bet.correct_count is None
                    else bet.correct_count
                ),
                (
                    ""
                    if bet.prize is None
                    else f"{bet.prize} kr"
                )
            )

            for column, value in enumerate(values):
                self.bet_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

    def update_bet_result_row(
        self,
        row,
        correct_count,
        prize
    ):
        """
            Uppdaterar resultat och vinst för en rad.
        """
        self.bet_table.setItem(
            row,
            self.COLUMN_CORRECT,
            QTableWidgetItem(str(correct_count))
        )

        self.bet_table.setItem(
            row,
            self.COLUMN_PRIZE,
            QTableWidgetItem(f"{prize} kr")
        )

    def get_selected_row(self):
        """
            Returnerar vald rad.
        """
        return self.bet_table.currentRow()
