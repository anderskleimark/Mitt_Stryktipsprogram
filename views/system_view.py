from PySide6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidgetItem,
                               QWidget)

from misc.base_table_widget import BaseTableWidget
from mvc import View


class SystemView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Tipssystem")
        self.layout.addWidget(self.header)

        self.layout.addSpacing(25)

        self.setLayout(self.layout)
        self.create_system_table()
        self.create_bottom_widget()

    def get_active_selection_table(self):
        return self.system_table

    # Funktion som skapar tabellen med tidigare tillagda tipssystem.
    def create_system_table(self):
        self.system_table = BaseTableWidget(True)
        self.system_table.setColumnCount(5)
        self.system_table.setHorizontalHeaderLabels([
            "Id",
            "Typ av system",
            "Helgarderingar",
            "Halvgarderingar",
            "Rader"
        ])

        # ID ska vara smal
        self.system_table.set_narrow_column(0)

        # Typ ska ta resten av utrymmet
        self.system_table.set_wide_column(1)

        # övriga kolumner
        for col in range(2, 5):
            self.system_table.set_narrow_column(col)

        self.layout.addWidget(self.system_table)

    # Funktion som uppdaterar tabellen med de olika tipssystemen.
    def update_systems(self, systems):
        self.system_table.clearContents()
        self.system_table.setRowCount(len(systems))

        for row, system in enumerate(systems):

            # ID (kan döljas om du vill senare)
            self.system_table.setItem(
                row,
                0,
                QTableWidgetItem(str(system.id))
            )

            self.system_table.setItem(
                row,
                1,
                QTableWidgetItem(system.type_name)
            )

            self.system_table.setItem(
                row,
                2,
                QTableWidgetItem(str(system.full_covers))
            )

            self.system_table.setItem(
                row,
                3,
                QTableWidgetItem(str(system.half_covers))
            )

            self.system_table.setItem(
                row,
                4,
                QTableWidgetItem(str(system.rows))
            )

    # Funktion som skapar panelen/widgeten under tabellen.
    def create_bottom_widget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Knappar
        self.add_system_button = QPushButton("Lägg till")
        layout.addWidget(self.add_system_button)
        self.delete_button = QPushButton("Radera")
        self.delete_button.setEnabled(False)
        self.delete_button.setProperty("buttonClass", "warning")
        layout.addWidget(self.delete_button)

        widget.setLayout(layout)
        self.layout.addWidget(widget)
