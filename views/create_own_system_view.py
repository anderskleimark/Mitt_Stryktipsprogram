from mvc import View
from models.coupon_model import Game
from widgets.year_week_widget import YearWeekWidget
from misc.base_table_widget import BaseTableWidget

from PySide6.QtCore import Qt, Signal

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QPushButton,
    QSpinBox,
    QComboBox,
    QProgressBar
)


class CreateOwnSystemView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.setLayout(self.layout)

        self.create_header("Skapa ett eget tipssystem")
        self.layout.addWidget(self.header)

        self.layout.addSpacing(25)
        self.create_top_widget()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()

        self.layout.addWidget(self.progress_bar)

    def create_top_widget(self):
        top_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        #
        # === RAD 1: FORMULÄR ===
        #
        form_layout = QHBoxLayout()
        form_layout.setSpacing(20)

        # Helgarderingar
        full_layout = QHBoxLayout()
        full_layout.addWidget(QLabel("Helgarderingar:"))

        self.full_cover_spin = QSpinBox()
        self.full_cover_spin.setRange(0, 13)
        self.full_cover_spin.setFixedWidth(60)
        full_layout.addWidget(self.full_cover_spin)

        form_layout.addLayout(full_layout)
        form_layout.addStretch()

        # Halvgarderingar
        half_layout = QHBoxLayout()
        half_layout.addWidget(QLabel("Halvgarderingar:"))

        self.half_cover_spin = QSpinBox()
        self.half_cover_spin.setRange(0, 13)
        self.half_cover_spin.setFixedWidth(60)
        half_layout.addWidget(self.half_cover_spin)

        form_layout.addLayout(half_layout)
        form_layout.addStretch()

        # Minsta garanti
        guarantee_layout = QHBoxLayout()
        guarantee_layout.addWidget(QLabel("Minsta garanti:"))

        self.min_guarantee_combo = QComboBox()
        self.min_guarantee_combo.addItems([
            "13 rätt",
            "12 rätt",
            "11 rätt",
            "10 rätt"
        ])
        self.min_guarantee_combo.setCurrentText("11 rätt")
        self.min_guarantee_combo.setFixedWidth(100)

        guarantee_layout.addWidget(self.min_guarantee_combo)

        form_layout.addLayout(guarantee_layout)
        form_layout.addStretch()

        # Antal rader
        rows_layout = QHBoxLayout()
        rows_layout.addWidget(QLabel("Antal rader:"))

        self.rows_combo = QComboBox()
        self.rows_combo.setEditable(True)
        self.rows_combo.setFixedWidth(90)

        self.rows_combo.addItems([
            "16", "32", "48", "64", "96", "128",
            "192", "256", "384", "512", "768",
            "1024", "1536", "2048", "4096",
            "8192", "16384"
        ])

        self.rows_combo.setCurrentText("128")
        rows_layout.addWidget(self.rows_combo)

        form_layout.addLayout(rows_layout)

        #
        # === RAD 2: KNAPP (VÄNSTERJUSTERAD) ===
        #
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 0)

        self.create_system_button = QPushButton("Skapa system")
        self.create_system_button.setMinimumWidth(160)

        button_layout.addWidget(self.create_system_button)
        button_layout.addStretch()

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        top_widget.setLayout(main_layout)
        self.layout.addWidget(top_widget)

    def start_progress(self):
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def stop_progress(self):
        self.progress_bar.hide()

    def show_system(self, system):
        print("test")
