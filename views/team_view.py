from PySide6.QtWidgets import (QComboBox, QFormLayout, QMessageBox,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import AddButton, DeleteButton, EditButton
from mvc import View


class TeamView(View):
    """
        Vyklass för visning och hantering av lag.
    """

    # --------------------------------------------------
    # Kolumner
    # --------------------------------------------------

    TEAM_TABLE_COLUMNS = 3

    COUNTRY_COLUMN = 0
    TEAM_COLUMN = 1
    DISPLAY_NAME_COLUMN = 2

    # --------------------------------------------------
    # Rubriker
    # --------------------------------------------------

    TEAM_TABLE_HEADERS = (
        "Land",
        "Lag",
        "Visningsnamn"
    )

    VIEW_TITLE = "Lag"
    COUNTRY_LABEL = "Land:"
    ALL_COUNTRIES_TEXT = "Alla länder"

    def __init__(self):
        """
        Initierar vyn och bygger gränssnittets komponenter.
        """
        super().__init__()

        self.layout = self.create_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self._create_top_form()
        self._create_team_table()
        self._create_bottom_panel()

        self.setLayout(self.layout)

    def _create_top_form(self):
        """
            Skapar formuläret med val av land.
        """
        self.country_combo = QComboBox()

        container = QWidget()
        layout = QFormLayout(container)

        layout.addRow(
            self.COUNTRY_LABEL,
            self.country_combo
        )

        self.layout.addWidget(container)

    def _create_team_table(self):
        """
            Skapar innehållswidgeten med lagtabellen.
        """
        self.team_table_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.team_table_widget,
            spacing=None
        )

        self.team_table = BaseTableWidget(
            True,
            True,
            0,
            self.TEAM_TABLE_COLUMNS
        )

        self.team_table.setHorizontalHeaderLabels(
            self.TEAM_TABLE_HEADERS
        )

        self.team_table.set_wide_columns([
            self.COUNTRY_COLUMN,
            self.TEAM_COLUMN,
            self.DISPLAY_NAME_COLUMN
        ])

        layout.addWidget(self.team_table)

        self.layout.addWidget(
            self.team_table_widget
        )

    def _create_bottom_panel(self):
        """
            Skapar knapppanelen för lagåtgärder.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_sub_layout(
            parent=self.bottom_widget,
            spacing=None
        )

        self.add_team_button = AddButton()
        layout.addWidget(self.add_team_button)

        self.edit_team_button = EditButton()
        layout.addWidget(self.edit_team_button)

        self.delete_team_button = DeleteButton()
        layout.addWidget(self.delete_team_button)

        self.set_button_status(False)

        self.layout.addWidget(
            self.bottom_widget
        )

    def update_country_combobox(self, countries: list["Country"]):
        """
            Uppdaterar listan över valbara länder.
        """
        self.country_combo.blockSignals(True)

        self.country_combo.clear()
        self.country_combo.addItem(
            self.ALL_COUNTRIES_TEXT
        )

        for country in countries:
            self.country_combo.addItem(
                country.country_name,
                country.id
            )

        self.country_combo.blockSignals(False)

    def show_teams(self, teams):
        """
            Visar en lista med lag i tabellen.
        """
        self.team_table.setRowCount(
            len(teams)
        )

        for row, team in enumerate(teams):
            country_item = QTableWidgetItem(
                team.country.display_name
            )

            country_item.setIcon(
                team.country.flag_icon
            )

            self.team_table.setItem(
                row,
                self.COUNTRY_COLUMN,
                country_item
            )

            self.team_table.setItem(
                row,
                self.TEAM_COLUMN,
                QTableWidgetItem(
                    team.team_name
                )
            )

            self.team_table.setItem(
                row,
                self.DISPLAY_NAME_COLUMN,
                QTableWidgetItem(
                    team.display_name
                )
            )

    def set_button_status(self, status):
        """
            Aktiverar eller inaktiverar åtgärdsknappar.
        """
        self.edit_team_button.setEnabled(
            status
        )

        self.delete_team_button.setEnabled(
            status
        )

    def get_selected_team_row(self):
        """
            Returnerar markerad rad i lagtavellen.
            Returnerar None om ingen rad är vald.
        """
        selected_rows = (
            self.team_table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        return selected_rows[0].row()

    def clear_selection(self):
        """
            Tar bort aktuell markering i lagtavellen.
        """
        self.team_table.clearSelection()

    def get_active_selection_table(self):
        """
            Returnerar tabellen som hanterar radmarkering.
        """
        return self.team_table

    def ask_delete_confirmation(self, team_name):
        """
            Visar en bekräftelsedialog innan ett lag tas bort.
            Returnerar True om användaren bekräftar.
        """
        reply = QMessageBox.question(
            self,
            "Ta bort lag",
            (
                f"Är du säker på att du vill ta bort laget\n\n"
                f"{team_name}?\n\n"
                "Åtgärden kan inte ångras."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return reply == QMessageBox.Yes
