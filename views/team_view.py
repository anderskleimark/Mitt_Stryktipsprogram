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


class TeamView(View):
    TEAM_TABLE_COLUMNS = 2
    COUNTRY_COLUMN = 0
    TEAM_COLUMN = 1
    BUTTON_ADD_TEXT = "Lägg till"
    BUTTON_DELETE_TEXT = "Ta bort"
    TEAM_TABLE_HEADERS = [
        "Land",
        "Lag"
    ]

    def __init__(self):
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
        self.country_combo = QComboBox()

        container = QWidget()
        layout = QFormLayout(container)

        layout.addRow("Land:", self.country_combo)

        self.layout.addWidget(container)

    def _create_team_table(self):
        self.team_table = BaseTableWidget(
            True, True, 0, self.TEAM_TABLE_COLUMNS)

        self.team_table.setColumnCount(self.TEAM_TABLE_COLUMNS)

        self.team_table.setHorizontalHeaderLabels(self.TEAM_TABLE_HEADERS)
        self.team_table.set_wide_columns(
            [
                self.COUNTRY_COLUMN,
                self.TEAM_COLUMN
            ]
        )
        self.layout.addWidget(self.team_table)

    def _create_bottom_panel(self):
        self.add_team_button = QPushButton(self.BUTTON_ADD_TEXT)
        self.delete_team_button = QPushButton(self.BUTTON_DELETE_TEXT)

        self.delete_team_button.setProperty(
            "buttonClass",
            "warning"
        )

        panel = QWidget()
        layout = QHBoxLayout(panel)

        layout.addWidget(self.add_team_button)
        layout.addWidget(self.delete_team_button)

        self.layout.addWidget(panel)

    def update_country_combobox(self, countries: list["Country"]):
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
