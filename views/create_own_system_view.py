from PySide6.QtWidgets import (QComboBox, QLabel, QProgressBar, QSpinBox,
                               QTableWidgetItem, QWidget)

from misc.base_table_widget import BaseTableWidget
from misc.buttons import CreateSystemButton
from mvc import View


class CreateOwnSystemView(View):
    """
        Vy för att skapa egna reducerade tipssystem.
    """

    # --------------------------------------------------
    # System
    # --------------------------------------------------

    MATCH_COUNT = 13

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Skapa ett eget tipssystem"

    FULL_COVER_LABEL = "Helgarderingar"
    HALF_COVER_LABEL = "Halvgarderingar"
    MIN_GUARANTEE_LABEL = "Minsta garanti"
    ROWS_LABEL = "Antal rader"

    # --------------------------------------------------
    # Garanti
    # --------------------------------------------------

    GUARANTEE_OPTIONS = (
        "13 rätt",
        "12 rätt",
        "11 rätt",
        "10 rätt"
    )

    DEFAULT_GUARANTEE = "11 rätt"

    # --------------------------------------------------
    # Rader
    # --------------------------------------------------

    ROW_OPTIONS = (
        "16",
        "32",
        "48",
        "64",
        "96",
        "128",
        "192",
        "256",
        "384",
        "512",
        "768",
        "1024",
        "1536",
        "2048",
        "4096",
        "8192",
        "16384"
    )

    DEFAULT_ROW_COUNT = "128"

    # --------------------------------------------------
    # Spinboxar
    # --------------------------------------------------

    SPIN_MIN = 0
    SPIN_MAX = 13

    # --------------------------------------------------
    # Storlekar
    # --------------------------------------------------

    SPIN_WIDTH = 60
    GUARANTEE_COMBO_WIDTH = 100
    ROWS_COMBO_WIDTH = 90

    CREATE_BUTTON_MIN_WIDTH = 160

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    FORM_SPACING = 20

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    PROGRESS_MIN = 0
    PROGRESS_MAX = 100

    def __init__(self):
        super().__init__()

        self.layout = self.create_main_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.create_form_widget()
        self.create_progress_widget()
        self.create_system_widget()
        self.create_bottom_widget()

        self.setLayout(self.layout)

    # --------------------------------------------------
    # Formulär
    # --------------------------------------------------

    def create_form_widget(self):
        """
            Skapar formuläret för systeminställningar.
        """
        self.form_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.form_widget,
            spacing=self.FORM_SPACING
        )

        # Helgarderingar
        full_layout = self.create_horizontal_layout(
            spacing=None
        )

        full_layout.addWidget(QLabel(self.FULL_COVER_LABEL))

        self.full_cover_spin = QSpinBox()

        self.full_cover_spin.setRange(
            self.SPIN_MIN,
            self.SPIN_MAX
        )

        self.full_cover_spin.setFixedWidth(self.SPIN_WIDTH)

        full_layout.addWidget(self.full_cover_spin)
        layout.addLayout(full_layout)

        layout.addStretch()

        # Halvgarderingar
        half_layout = self.create_horizontal_layout(
            spacing=None
        )

        half_layout.addWidget(QLabel(self.HALF_COVER_LABEL))

        self.half_cover_spin = QSpinBox()

        self.half_cover_spin.setRange(
            self.SPIN_MIN,
            self.SPIN_MAX
        )

        self.half_cover_spin.setFixedWidth(self.SPIN_WIDTH)

        half_layout.addWidget(self.half_cover_spin)

        layout.addLayout(half_layout)

        layout.addStretch()

        # Minsta garanti
        guarantee_layout = self.create_horizontal_layout(
            spacing=None
        )

        guarantee_layout.addWidget(
            QLabel(self.MIN_GUARANTEE_LABEL)
        )

        self.min_guarantee_combo = QComboBox()
        self.min_guarantee_combo.addItems(self.GUARANTEE_OPTIONS)
        self.min_guarantee_combo.setCurrentText(self.DEFAULT_GUARANTEE)

        self.min_guarantee_combo.setFixedWidth(self.GUARANTEE_COMBO_WIDTH)

        guarantee_layout.addWidget(self.min_guarantee_combo)
        layout.addLayout(guarantee_layout)

        layout.addStretch()

        # Antal rader
        rows_layout = self.create_horizontal_layout(
            spacing=None
        )

        rows_layout.addWidget(QLabel(self.ROWS_LABEL))

        self.rows_combo = QComboBox()
        self.rows_combo.setEditable(True)

        self.rows_combo.addItems(self.ROW_OPTIONS)
        self.rows_combo.setCurrentText(self.DEFAULT_ROW_COUNT)

        self.rows_combo.setFixedWidth(self.ROWS_COMBO_WIDTH)

        rows_layout.addWidget(self.rows_combo)

        layout.addLayout(rows_layout)

        self.layout.addWidget(self.form_widget)

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def create_progress_widget(self):
        """
            Skapar widgeten med progressbaren.
        """
        self.progress_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.progress_widget,
            spacing=None
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            self.PROGRESS_MIN,
            self.PROGRESS_MAX
        )

        self.progress_bar.hide()

        layout.addWidget(self.progress_bar)

        self.layout.addWidget(self.progress_widget)

    # --------------------------------------------------
    # Systemtabell
    # --------------------------------------------------

    def create_system_widget(self):
        """
            Skapar widgeten som visar genererade system.
        """
        self.system_widget = QWidget()

        layout = self.create_vertical_layout(
            parent=self.system_widget,
            spacing=None
        )

        self.system_table = BaseTableWidget(
            True,
            False,
            self.MATCH_COUNT
        )

        self.system_table.set_no_selection()

        layout.addWidget(self.system_table)
        self.layout.addWidget(self.system_widget)

    # --------------------------------------------------
    # Bottenpanel
    # --------------------------------------------------

    def create_bottom_widget(self):
        """
            Skapar den nedre knappraden.
        """
        self.bottom_widget = QWidget()

        layout = self.create_horizontal_layout(
            parent=self.bottom_widget,
            spacing=None
        )

        self.create_system_button = CreateSystemButton()
        self.create_system_button.setMinimumWidth(self.CREATE_BUTTON_MIN_WIDTH)

        layout.addWidget(self.create_system_button)

        self.layout.addWidget(self.bottom_widget)

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def start_progress(self):
        """
            Startar progressbaren.
        """
        self.progress_bar.setValue(self.PROGRESS_MIN)

        self.progress_bar.show()

    def set_progress(
        self,
        value
    ):
        """
            Sätter progressbaren till angivet värde.
        """
        self.progress_bar.setValue(
            value
        )

    def stop_progress(self):
        """
            Döljer progressbaren.
        """
        self.progress_bar.hide()

    # --------------------------------------------------
    # System
    # --------------------------------------------------

    def show_system(
        self,
        system
    ):
        """
            Visar det genererade systemet transponerat.
        """
        rows = system["rows"]

        if not rows:
            return

        match_count = len(rows[0])
        row_count = len(rows)

        self.system_table.clearContents()
        self.system_table.setRowCount(match_count)
        self.system_table.setColumnCount(row_count)

        self.system_table.setVerticalHeaderLabels(
            [
                f"Match {index + 1}"
                for index in range(match_count)
            ]
        )

        self.system_table.setHorizontalHeaderLabels(
            [
                f"Rad {index + 1}"
                for index in range(row_count)
            ]
        )

        for row in range(match_count):
            for column in range(row_count):
                self.system_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(rows[column][row])
                    )
                )

        self.system_widget.show()

    def get_active_selection_table(self):
        """
            Returnerar den aktiva tabellen.
        """
        return self.system_table
