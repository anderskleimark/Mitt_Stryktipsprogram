from mvc import Model, View, Controller
from models.coupon_model import Game
from widgets.year_week_widget import YearWeekWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
    QPushButton
)


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

    # Funktion som skapar tabellen med tidigare tillagda tipssystem.
    def create_system_table(self):
        self.system_table = QTableWidget()
        self.register_selection_table(self.system_table)

        self.system_table.setColumnCount(5)
        self.system_table.setHorizontalHeaderLabels([
            "Id",
            "Typ av system",
            "Helgarderingar",
            "Halvgarderingar",
            "Rader"
        ])

        header = self.system_table.horizontalHeader()

        # ID ska vara smal
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        # Typ ska ta resten av utrymmet
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        # övriga kolumner
        for col in range(2, 5):
            header.setSectionResizeMode(
                col,
                QHeaderView.ResizeMode.ResizeToContents
            )

        self.system_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.system_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.system_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.system_table.setAlternatingRowColors(True)
        self.system_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)

        self.system_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

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
