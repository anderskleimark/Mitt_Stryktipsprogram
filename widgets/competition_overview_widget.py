from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidgetItem

from misc.base_table_widget import BaseTableWidget

from widgets.base_widget import BaseWidget


class CompetitionOverviewWidget(BaseWidget):
    """
        Widget som visar en översikt över
        tävlingar och ligor.
    """
    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    competition_changed = Signal()

    # --------------------------------------------------
    # Tabell
    # --------------------------------------------------

    # Tabellrubriker
    HEADERS = [
        "Id",
        "Land",
        "Namn"
    ]

    # Kolumner - tävlingar
    ID_COLUMN = 0
    COUNTRY_COLUMN = 1
    NAME_COLUMN = 2

    def __init__(self):
        """
            Initierar widgeten och skapar
            tabellen samt signalanslutningarna.
        """
        super().__init__()
        self._build_widget()
        self._setup_signals()

    def _build_widget(self):
        """
            Skapar widgetens layout och tabellen med tävlingar.
        """
        layout = self.create_vertical_layout(
            parent=self,
            spacing=None
        )

        self.table = BaseTableWidget(
            readonly=True,
            rowselection=True
        )

        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)

        self.table.set_narrow_columns([
            self.ID_COLUMN,
            self.COUNTRY_COLUMN
        ])

        self.table.set_wide_column(self.NAME_COLUMN)

        layout.addWidget(self.table)
        layout.addSpacing(1)

    def _setup_signals(self):
        """
            Kopplar tabellens markeringssignal till widgetens egen signal.
        """
        self.table.itemSelectionChanged.connect(self.competition_changed.emit)

    def update_table(self, competitions):
        """
            Uppdaterar tabellen med tävlingar.
        """
        self.table.blockSignals(True)
        self.table.clear_current_selection()
        self.table.clearContents()
        self.table.setRowCount(len(competitions))

        for row, competition in enumerate(competitions):
            # Id
            self.table.setItem(
                row,
                self.ID_COLUMN,
                QTableWidgetItem(str(competition.id))
            )

            # Land med flagga
            country_item = QTableWidgetItem(competition.country.display_name)
            country_item.setIcon(competition.country.flag_icon)

            self.table.setItem(
                row,
                self.COUNTRY_COLUMN,
                country_item
            )

            # Namn
            self.table.setItem(
                row,
                self.NAME_COLUMN,
                QTableWidgetItem(competition.competition_name)
            )

        # Anpassa kolumnbredder
        self.table.set_narrow_columns(
            [
                self.ID_COLUMN
            ]
        )

        self.table.set_wide_columns(
            [
                self.COUNTRY_COLUMN,
                self.NAME_COLUMN
            ]
        )
        self.table.blockSignals(False)

    def get_selected_row(self):
        """
            Returnerar index för den markerade raden.

            Returnerar -1 om ingen rad
            är markerad.
        """
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            return -1

        return selected_rows[0].row()

    def get_active_selection_table(self):
        """
            Returnerar tävlingstabellen om den har
            en aktiv markering.
        """
        if self.table.selectedItems():
            return self.table

        return None

    def clear_current_selection(self):
        self.table.clear_current_selection()
