from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTableWidgetItem, QWidget

from misc.base_table_widget import BaseTableWidget
from widgets.base_widget import BaseWidget


class FormWidget(BaseWidget):
    """
        Widget för att visa form.
    """

    FORM_LABEL = "Form"
    HOME_TEAM = "Hemmalag"
    AWAY_TEAM = "Bortalag"
    RESULT = "Resulat"
    DATE = "Datum"

    HOME_TEAM_COLUMN = 0
    AWAY_TEAM_COLUMN = 1
    DATE_COLUMN = 2
    RESULT_COLUMN = 3

    def __init__(self):
        """
            Initierar widgeten för visning av form / de senaste matcherna.
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
        self.form_label = QLabel(self.FORM_LABEL)
        self.form_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_widget = QWidget()
        self.create_tables()

    def create_tables(self):
        headers = [
            self.HOME_TEAM,
            self.AWAY_TEAM,
            self.DATE,
            self.RESULT
        ]
        self.home_team_table = BaseTableWidget(
            headers=headers,
            readonly=True,
            selection=False
        )
        self.away_team_table = BaseTableWidget(headers=headers)

        for table in (self.home_team_table, self.away_team_table):
            table.set_wide_columns(
                [self.HOME_TEAM_COLUMN, self.AWAY_TEAM_COLUMN])
            table.set_narrow_columns([self.DATE_COLUMN, self.RESULT_COLUMN])

    def create_layout(self):
        layout = self.create_vertical_layout(parent=self)
        layout.addWidget(self.form_label)

        self.table_layout = self.create_horizontal_layout(
            parent=self.table_widget
        )

        self.table_layout.addWidget(self.home_team_table)
        self.table_layout.addWidget(self.away_team_table)

        layout.addWidget(self.table_widget)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(self, analysis):
        """
            Visar matcherna som används för formberäkningen.
        """
        self.fill_table(
            self.home_team_table,
            analysis.home_form_matches
        )

        self.fill_table(
            self.away_team_table,
            analysis.away_form_matches
        )

    def fill_table(self, table, matches):
        """
            Fyller en tabell med formmatcher.
        """
        table.setRowCount(len(matches))

        for row, match in enumerate(matches):
            table.setItem(
                row,
                self.HOME_TEAM_COLUMN,
                QTableWidgetItem(match.home_team.display_name)
            )

            table.setItem(
                row,
                self.AWAY_TEAM_COLUMN,
                QTableWidgetItem(match.away_team.display_name)
            )

            table.setItem(
                row,
                self.DATE_COLUMN,
                QTableWidgetItem(
                    f"{match.match_date.day}/{match.match_date.month}"
                )
            )

            table.setItem(
                row,
                self.RESULT_COLUMN,
                QTableWidgetItem(
                    f"{match.home_score} - {match.away_score}"
                )
            )

            table.center_columns([self.RESULT_COLUMN])

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_analysis(self):
        """
            Tömmer formtabellerna.
        """
        self.home_team_table.setRowCount(0)
        self.away_team_table.setRowCount(0)
