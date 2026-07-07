from mvc import View
from models.coupon_model import Match
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

# Klass (Vy), som visar data, när användaren skapar egna reducerade tipssystem.


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

        self.create_system_widget()

        self.layout.addWidget(self.progress_bar)

    # Funktion som skapar den översta widgeten.
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

    # Funktion som skapar widgeten, som visar de system som skapas av användaren.
    def create_system_widget(self):

        self.system_widget = QWidget()
        layout = QVBoxLayout()

        self.system_table = QTableWidget()
        self.system_table.setColumnCount(13)  # Stryktipset = 13 matcher
        self.system_table.setHorizontalHeaderLabels(
            [str(i+1) for i in range(13)]
        )

        self.system_table.setSizeAdjustPolicy(
            QTableWidget.AdjustToContents
        )

        layout.addWidget(self.system_table)
        self.system_widget.setLayout(layout)

        self.layout.addWidget(self.system_widget)

    # Funktion som startar "progress bar".
    def start_progress(self):
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    # Funktion för att sätta "progress bar" på ett specifikt värde.
    def set_progress(self, value):
        self.progress_bar.setValue(value)

    # Funktion för att stoppa "progress bar".
    def stop_progress(self):
        self.progress_bar.hide()

    # Funktion för att visa de system som skapats.
    def show_system(self, system):
        rows = system["rows"]

        if not rows:
            return

        num_matches = len(rows[0])  # 13
        num_system_rows = len(rows)

        # vi visar "vänd version"
        self.system_table.clear()
        self.system_table.setRowCount(num_matches)
        self.system_table.setColumnCount(num_system_rows)

        # sätt headers (valfritt men bra)
        self.system_table.setVerticalHeaderLabels(
            [f"Match {i+1}" for i in range(num_matches)]
        )

        self.system_table.setHorizontalHeaderLabels(
            [f"Rad {i+1}" for i in range(num_system_rows)]
        )

        # fyll transponerat
        for r in range(num_matches):
            for c in range(num_system_rows):
                self.system_table.setItem(
                    r,
                    c,
                    QTableWidgetItem(str(rows[c][r]))
                )

        self.system_widget.show()
