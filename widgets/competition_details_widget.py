from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QTableWidgetItem

from misc.base_table_widget import BaseTableWidget
from misc.buttons import AddButton, DeleteButton

from widgets.base_widget import BaseWidget


class CompetitionDetailsWidget(BaseWidget):
    """
        Widget som visar detaljer för en vald
        tävling.

        Widgeten innehåller säsongstabell,
        lagtabell samt knappar för att lägga
        till och ta bort säsonger och lag.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    season_changed = Signal()
    team_changed = Signal()

    # --------------------------------------------------
    # Kolumner - säsonger
    # --------------------------------------------------

    SEASON_ID_COLUMN = 0
    SEASON_NAME_COLUMN = 1

    # --------------------------------------------------
    # Kolumner - lag
    # --------------------------------------------------

    TEAM_ID_COLUMN = 0
    TEAM_NAME_COLUMN = 1

    # --------------------------------------------------
    # Tabellrubriker
    # --------------------------------------------------

    SEASON_HEADERS = [
        "Id",
        "Säsong"
    ]

    TEAM_HEADERS = [
        "Id",
        "Lag"
    ]

    def __init__(self):
        """
            Initierar widgeten och skapar
            dess innehåll och signalanslutningar.
        """
        super().__init__()

        self._build_widget()
        self._setup_signals()

    def _build_widget(self):
        """
            Skapar widgetens layout, tabeller
            och knappar.

            Den övre delen innehåller säsonger
            och den nedre delen innehåller lag
            för den valda säsongen.
        """
        layout = self.create_vertical_layout(parent=self)

        # Säsonger
        layout.addWidget(QLabel("Säsonger"))

        self.season_table = BaseTableWidget(
            readonly=True,
            rowselection=True
        )

        self.season_table.setColumnCount(len(self.SEASON_HEADERS))
        self.season_table.setHorizontalHeaderLabels(self.SEASON_HEADERS)
        self.season_table.set_narrow_column(self.SEASON_ID_COLUMN)
        self.season_table.set_wide_column(self.SEASON_NAME_COLUMN)

        layout.addWidget(self.season_table)

        # Knappar för säsonger
        season_buttons = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        self.add_season_button = AddButton()
        season_buttons.addWidget(self.add_season_button)

        self.delete_season_button = DeleteButton()
        season_buttons.addWidget(self.delete_season_button)

        season_buttons.addStretch()
        layout.addLayout(season_buttons)

        # Lag
        layout.addWidget(QLabel("Lag"))

        self.team_table = BaseTableWidget(
            True,
            True
        )

        self.team_table.setColumnCount(len(self.TEAM_HEADERS))

        self.team_table.setHorizontalHeaderLabels(self.TEAM_HEADERS)

        self.team_table.set_narrow_column(self.TEAM_ID_COLUMN)

        self.team_table.set_wide_column(self.TEAM_NAME_COLUMN)

        layout.addWidget(self.team_table)

        # Knappar för lag
        team_buttons = self.create_horizontal_layout(
            parent=None,
            spacing=None
        )

        self.add_team_button = AddButton()

        team_buttons.addWidget(self.add_team_button)

        self.delete_team_button = DeleteButton()
        team_buttons.addWidget(self.delete_team_button)

        team_buttons.addStretch()

        layout.addLayout(team_buttons)

    def _setup_signals(self):
        """
            Vidarebefordrar ändringar av markering i säsongs- och lagtabellen genom
            widgetens egna signaler.
        """
        self.season_table.itemSelectionChanged.connect(
            self.season_changed.emit)

        self.team_table.itemSelectionChanged.connect(self.team_changed.emit)

    # --------------------------------------------------
    # Uppdatering
    # --------------------------------------------------

    def update_season_table(
        self,
        seasons
    ):
        """
            Uppdaterar säsongstabellen med
            angivna säsonger.
        """
        self.season_table.clearContents()

        self.season_table.setRowCount(len(seasons))

        for row, season in enumerate(
            seasons
        ):
            self.season_table.setItem(
                row,
                self.SEASON_ID_COLUMN,
                QTableWidgetItem(str(season.id))
            )

            self.season_table.setItem(
                row,
                self.SEASON_NAME_COLUMN,
                QTableWidgetItem(season.name)
            )

        self.season_table.set_narrow_column(self.SEASON_ID_COLUMN)
        self.season_table.set_wide_column(self.SEASON_NAME_COLUMN)

    def update_team_table(
        self,
        teams
    ):
        """
            Uppdaterar lagtabellen med angivna lag.
        """
        self.team_table.clearContents()
        self.team_table.setRowCount(len(teams))

        for row, team in enumerate(
            teams
        ):
            self.team_table.setItem(
                row,
                self.TEAM_ID_COLUMN,
                QTableWidgetItem(str(team.id))
            )

            self.team_table.setItem(
                row,
                self.TEAM_NAME_COLUMN,
                QTableWidgetItem(team.team_name)
            )

        self.team_table.set_narrow_column(self.TEAM_ID_COLUMN)
        self.team_table.set_wide_column(self.TEAM_NAME_COLUMN)

    # --------------------------------------------------
    # Markering
    # --------------------------------------------------

    def clear_season_selection(self):
        """
            Rensar markeringen i säsongstabellen.
        """
        self.season_table.clearSelection()

    def clear_team_selection(self):
        """
            Rensar markeringen i lagtabellen.
        """
        self.team_table.clearSelection()

    def get_selected_season_row(self):
        """
            Returnerar vald rad i säsongstabellen.

            Returnerar -1 om ingen rad är markerad.
        """
        return self.season_table.get_selected_row()

    def get_selected_team_row(self):
        """
            Returnerar vald rad i lagtabellen.

            Returnerar -1 om ingen rad är markerad.
        """
        return self.team_table.get_selected_row()

    def get_active_selection_table(self):
        """
            Returnerar den tabell i widgeten som för närvarande har en markering.

            Returnerar None om ingen av tabellerna har en aktiv markering.
        """
        if self.season_table.selectedItems():
            return self.season_table

        if self.team_table.selectedItems():
            return self.team_table

        return None
