from PySide6.QtWidgets import QTableWidgetItem, QWidget

from misc.base_table_widget import BaseTableWidget
from misc.buttons import AddButton, DeleteButton
from misc.dialogs.add_system_dialog import AddSystemDialog
from mvc import View


class SystemView(View):
    """
        Vy för att visa och hantera reducerade tipssystem.
    """

    COLUMN_ID = 0
    COLUMN_TYPE = 1
    COLUMN_FULL_COVERS = 2
    COLUMN_HALF_COVERS = 3
    COLUMN_ROWS = 4

    COLUMN_COUNT = 5

    TABLE_HEADERS = (
        "Id",
        "Typ av system",
        "Helgarderingar",
        "Halvgarderingar",
        "Rader"
    )

    VIEW_TITLE = "Tipssystem"

    def __init__(self):
        super().__init__()

        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)

        self.layout.addWidget(self.header)

        self.create_system_table()
        self.create_bottom_widget()

        self.add_bottom_panel(self.bottom_widget)

        self.setLayout(self.layout)

    def create_system_table(self):
        """
            Skapar innehållswidgeten med systemtabellen.
        """
        self.system_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.system_widget,
            spacing=None
        )

        self.system_table = BaseTableWidget(
            True,
            True,
            self.COLUMN_COUNT
        )

        self.system_table.setHorizontalHeaderLabels(self.TABLE_HEADERS)

        self.system_table.set_narrow_column(self.COLUMN_ID)

        self.system_table.set_wide_column(self.COLUMN_TYPE)

        self.system_table.set_narrow_columns(
            [
                self.COLUMN_FULL_COVERS,
                self.COLUMN_HALF_COVERS,
                self.COLUMN_ROWS
            ]
        )

        layout.addWidget(self.system_table)

        self.layout.addWidget(
            self.system_widget,
            stretch=self.FULL_STRETCH
        )

    def create_bottom_widget(self):
        """
            Skapar den nedre knappraden.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.bottom_widget,
            spacing=None
        )

        self.add_system_button = AddButton()
        layout.addWidget(self.add_system_button)

        self.delete_button = DeleteButton()
        layout.addWidget(self.delete_button)

    def update_systems(self, systems):
        self.system_table.clearContents()
        self.system_table.setRowCount(len(systems))

        for row, system in enumerate(systems):
            values = (
                system.id,
                system.type_name,
                system.full_covers,
                system.half_covers,
                system.row_count
            )

            for column, value in enumerate(values):
                self.system_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value))
                )

    def show_add_system_dialog(self):
        """
            Visar dialogen för att lägga till ett system.
        """
        dialog = AddSystemDialog(parent=self)

        if not dialog.exec():
            return None

        return (
            dialog.system_type,
            dialog.full_covers,
            dialog.half_covers,
            dialog.row_count
        )

    def get_active_selection_table(self):
        return self.system_table
