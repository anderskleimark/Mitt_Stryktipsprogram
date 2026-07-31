from mvc import View
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHeaderView,
    QWidget,
    QTableWidget,
    QVBoxLayout,
    QLabel
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton
)
from misc.base_table_widget import BaseTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox


class TeamView(View):
    """
        Vyklass för visning och hantering av lag.
    """
    TEAM_TABLE_COLUMNS = 3
    COUNTRY_COLUMN = 0
    TEAM_COLUMN = 1
    DISPLAY_NAME_COLUMN = 2
    BUTTON_ADD_TEXT = "Lägg till"
    BUTTON_DELETE_TEXT = "Ta bort"
    BUTTON_EDIT_TEXT = "Redigera"
    TEAM_TABLE_HEADERS = [
        "Land",
        "Lag",
        "Visningsnamn"
    ]

    def __init__(self):
        """
            Initierar vyn och bygger gränssnittets komponenter.
        """
        super().__init__()

        self.add_team_button = None
        self.delete_team_button = None
        self.team_table = None

        self.layout = self.create_layout()
        self.create_header("Lag")
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

        layout.addRow("Land:", self.country_combo)

        self.layout.addWidget(container)

    def _create_team_table(self):
        """
            Skapar tabellen som visar laginformation.
        """
        self.team_table = BaseTableWidget(
            True, True, 0, self.TEAM_TABLE_COLUMNS)

        self.team_table.setColumnCount(self.TEAM_TABLE_COLUMNS)

        self.team_table.setHorizontalHeaderLabels(self.TEAM_TABLE_HEADERS)
        self.team_table.set_wide_columns(
            [
                self.COUNTRY_COLUMN,
                self.TEAM_COLUMN,
                self.DISPLAY_NAME_COLUMN
            ]
        )
        self.layout.addWidget(self.team_table)

    def _create_bottom_panel(self):
        """
            Skapar knapppanelen för lagåtgärder.
        """
        self.add_team_button = QPushButton(self.BUTTON_ADD_TEXT)
        self.edit_team_button = QPushButton(self.BUTTON_EDIT_TEXT)
        self.delete_team_button = QPushButton(self.BUTTON_DELETE_TEXT)
        self.set_button_status(False)

        self.delete_team_button.setProperty(
            "buttonClass",
            "warning"
        )

        panel = QWidget()
        layout = QHBoxLayout(panel)

        layout.addWidget(self.add_team_button)
        layout.addWidget(self.edit_team_button)
        layout.addWidget(self.delete_team_button)

        self.layout.addWidget(panel)

    def update_country_combobox(self, countries: list["Country"]):
        """
            Uppdaterar listan över valbara länder.
        """
        self.blockSignals(True)
        self.country_combo.clear()
        self.country_combo.addItem("Alla länder")
        for country in countries:
            self.country_combo.addItem(
                country.country_name,
                country.id
            )
        self.blockSignals(False)

    def show_teams(self, teams):
        """
            Visar en lista med lag i tabellen.
        """
        self.team_table.setRowCount(len(teams))

        for row, team in enumerate(teams):
            # Land med flagga
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

            # Lag
            self.team_table.setItem(
                row,
                self.TEAM_COLUMN,
                QTableWidgetItem(
                    team.team_name
                )
            )

            # Visningsnamn
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
        self.edit_team_button.setEnabled(status)
        self.delete_team_button.setEnabled(status)

    def get_selected_team_row(self):
        """
            Returnerar markerad rad i lagtavellen.
            Returnerar None om ingen rad är vald.
        """
        selected_rows = (
            self.team_table.selectionModel().selectedRows()
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
