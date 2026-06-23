from mvc import Model, View, Controller
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton
)


class AddCouponView(View):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Lägg till en kupong")
        header.setFont(self.header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # År och vecka
        form_widget = QWidget()
        form_layout = QGridLayout()

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(2000, 2100)
        self.year_spinbox.setValue(2026)

        self.week_spinbox = QSpinBox()
        self.week_spinbox.setRange(1, 53)

        form_layout.addWidget(QLabel("År"), 0, 0)
        form_layout.addWidget(self.year_spinbox, 0, 1)

        form_layout.addWidget(QLabel("Vecka"), 0, 2)
        form_layout.addWidget(self.week_spinbox, 0, 3)

        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        # Matchtabell
        self.matches_table = QTableWidget(13, 2)

        self.matches_table.setHorizontalHeaderLabels(
            ["Hemmalag", "Bortalag"]
        )

        self.matches_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Matchnummer som radrubriker
        for row in range(13):
            self.matches_table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(row + 1))
            )

        layout.addWidget(self.matches_table)

        # Spara-knapp
        self.save_button = QPushButton("Spara kupong")
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def update(self, model):
        pass
