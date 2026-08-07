from PySide6.QtWidgets import (QComboBox, QLabel, QProgressBar, QSpinBox,
                               QTableWidget, QTableWidgetItem, QWidget)

from misc.buttons import CreateSystemButton
from mvc import View


class CreateOwnSystemView(View):
    """
        Vy för att skapa egna reducerade tipssystem.
    """

    # --------------------------------------------------
    # Konstanter
    # --------------------------------------------------

    MATCH_COUNT = 13

    VIEW_TITLE = "Skapa ett eget tipssystem"

    FULL_COVER_LABEL = "Helgarderingar:"
    HALF_COVER_LABEL = "Halvgarderingar:"
    MIN_GUARANTEE_LABEL = "Minsta garanti:"
    ROWS_LABEL = "Antal rader:"

    GUARANTEE_OPTIONS = (
        "13 rätt",
        "12 rätt",
        "11 rätt",
        "10 rätt"
    )

    DEFAULT_GUARANTEE = "11 rätt"

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

    SPIN_MIN = 0
    SPIN_MAX = 13

    SPIN_WIDTH = 60
    GUARANTEE_COMBO_WIDTH = 100
    ROWS_COMBO_WIDTH = 90

    CREATE_BUTTON_MIN_WIDTH = 160

    FORM_SPACING = 20
    BUTTON_TOP_SPACING = 15

    PROGRESS_MIN = 0
    PROGRESS_MAX = 100

    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self.create_top_widget()

        self.create_progress_bar()
        self.create_system_widget()

        self.setLayout(self.layout)

    def create_top_widget(self):
        """
            Skapar formulär och knapp för systemgenerering.
        """
        self.top_widget = QWidget()

        main_layout = self.create_vertical_sub_layout(
            parent=self.top_widget,
            spacing=None
        )

        form_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=self.FORM_SPACING
        )

        # Helgarderingar
        full_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=None
        )

        full_layout.addWidget(
            QLabel(self.FULL_COVER_LABEL)
        )

        self.full_cover_spin = QSpinBox()
        self.full_cover_spin.setRange(
            self.SPIN_MIN,
            self.SPIN_MAX
        )
        self.full_cover_spin.setFixedWidth(
            self.SPIN_WIDTH
        )

        full_layout.addWidget(
            self.full_cover_spin
        )

        form_layout.addLayout(full_layout)
        form_layout.addStretch()

        # Halvgarderingar
        half_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=None
        )

        half_layout.addWidget(
            QLabel(self.HALF_COVER_LABEL)
        )

        self.half_cover_spin = QSpinBox()
        self.half_cover_spin.setRange(
            self.SPIN_MIN,
            self.SPIN_MAX
        )
        self.half_cover_spin.setFixedWidth(
            self.SPIN_WIDTH
        )

        half_layout.addWidget(
            self.half_cover_spin
        )

        form_layout.addLayout(half_layout)
        form_layout.addStretch()

        # Minsta garanti
        guarantee_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=None
        )

        guarantee_layout.addWidget(
            QLabel(self.MIN_GUARANTEE_LABEL)
        )

        self.min_guarantee_combo = QComboBox()
        self.min_guarantee_combo.addItems(
            self.GUARANTEE_OPTIONS
        )
        self.min_guarantee_combo.setCurrentText(
            self.DEFAULT_GUARANTEE
        )
        self.min_guarantee_combo.setFixedWidth(
            self.GUARANTEE_COMBO_WIDTH
        )

        guarantee_layout.addWidget(
            self.min_guarantee_combo
        )

        form_layout.addLayout(guarantee_layout)
        form_layout.addStretch()

        # Antal rader
        rows_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=None
        )

        rows_layout.addWidget(
            QLabel(self.ROWS_LABEL)
        )

        self.rows_combo = QComboBox()
        self.rows_combo.setEditable(True)
        self.rows_combo.setFixedWidth(
            self.ROWS_COMBO_WIDTH
        )

        self.rows_combo.addItems(
            self.ROW_OPTIONS
        )

        self.rows_combo.setCurrentText(
            self.DEFAULT_ROW_COUNT
        )

        rows_layout.addWidget(
            self.rows_combo
        )

        form_layout.addLayout(rows_layout)

        main_layout.addLayout(form_layout)

        # Knapp
        button_layout = self.create_horizontal_sub_layout(
            parent=None,
            spacing=None
        )

        button_layout.addSpacing(
            self.BUTTON_TOP_SPACING
        )

        self.create_system_button = CreateSystemButton()

        self.create_system_button.setMinimumWidth(
            self.CREATE_BUTTON_MIN_WIDTH
        )

        button_layout.addWidget(
            self.create_system_button
        )

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        self.layout.addWidget(
            self.top_widget
        )

    def create_progress_bar(self):
        """
            Skapar progressbaren.
        """
        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            self.PROGRESS_MIN,
            self.PROGRESS_MAX
        )

        self.progress_bar.hide()

        self.layout.addWidget(
            self.progress_bar
        )

    def create_system_widget(self):
        """
            Skapar widgeten som visar genererade system.
        """
        self.system_widget = QWidget()

        layout = self.create_vertical_sub_layout(
            parent=self.system_widget,
            spacing=None
        )

        self.system_table = QTableWidget(
            0,
            self.MATCH_COUNT
        )

        self.system_table.setHorizontalHeaderLabels(
            [
                str(index + 1)
                for index in range(self.MATCH_COUNT)
            ]
        )

        self.system_table.setSizeAdjustPolicy(
            QTableWidget.SizeAdjustPolicy.AdjustToContents
        )

        layout.addWidget(
            self.system_table
        )

        self.layout.addWidget(
            self.system_widget
        )

    def start_progress(self):
        """
            Startar progressbaren.
        """
        self.progress_bar.setValue(
            self.PROGRESS_MIN
        )

        self.progress_bar.show()

    def set_progress(self, value):
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

    def show_system(self, system):
        """
        Visar det genererade systemet transponerat.
        """
        rows = system["rows"]

        if not rows:
            return

        num_matches = len(rows[0])
        num_system_rows = len(rows)

        self.system_table.clear()

        self.system_table.setRowCount(
            num_matches
        )

        self.system_table.setColumnCount(
            num_system_rows
        )

        self.system_table.setVerticalHeaderLabels(
            [
                f"Match {index + 1}"
                for index in range(num_matches)
            ]
        )

        self.system_table.setHorizontalHeaderLabels(
            [
                f"Rad {index + 1}"
                for index in range(num_system_rows)
            ]
        )

        for row in range(num_matches):
            for column in range(num_system_rows):
                self.system_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(rows[column][row])
                    )
                )

        self.system_widget.show()
