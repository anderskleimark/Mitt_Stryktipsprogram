from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDoubleSpinBox, QFormLayout, QLabel, QSpinBox,
                               QWidget)

from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class SettingView(View):
    """
        Vy för att visa och hantera inställningar.
    """

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    font_changed = Signal(str)

    history_years_changed = Signal(int)
    time_decay_changed = Signal(float)
    training_scope_changed = Signal(str)

    form_match_count_changed = Signal(int)
    form_weight_changed = Signal(float)

    h2h_match_count_changed = Signal(int)
    h2h_weight_changed = Signal(float)

    rho_mode_changed = Signal(str)

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    VIEW_TITLE = "Inställningar"

    FONT_LABEL = "Typsnitt"

    HISTORY_YEARS_LABEL = "Historiklängd"
    TIME_DECAY_LABEL = "Time decay"
    TRAINING_SCOPE_LABEL = "Träningsdata"

    FORM_MATCH_COUNT_LABEL = "Antal formmatcher"
    FORM_WEIGHT_LABEL = "Formvikt"

    H2H_MATCH_COUNT_LABEL = "Antal H2H-matcher"
    H2H_WEIGHT_LABEL = "H2H-vikt"

    RHO_MODE_LABEL = "Rho-läge"

    # --------------------------------------------------
    # Värden
    # --------------------------------------------------

    TRAINING_SCOPE_COUNTRY = "country"
    TRAINING_SCOPE_COMPETITION = "competition"

    RHO_MODE_FIXED = "fixed"
    RHO_MODE_ESTIMATED = "estimated"

    INGRESS_ALIGNMENT = (
        Qt.AlignmentFlag.AlignHCenter
        | Qt.AlignmentFlag.AlignTop
    )

    def __init__(self):
        super().__init__()

        self.layout = self.create_main_layout()

        self.font_combo_box = None

        self.history_years_spin_box = None
        self.time_decay_spin_box = None
        self.training_scope_combo_box = None

        self.form_match_count_spin_box = None
        self.form_weight_spin_box = None

        self.h2h_match_count_spin_box = None
        self.h2h_weight_spin_box = None

        self.rho_mode_combo_box = None

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)

        self._create_ingress_widget()
        self._create_form_widget()

        self.setLayout(self.layout)

        self._setup_signals()

    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    def _setup_signals(self):
        """
            Kopplar widgetarnas signaler till
            vyklassens egna signaler.
        """
        self.font_combo_box.currentTextChanged.connect(
            self.font_changed.emit
        )

        self.history_years_spin_box.valueChanged.connect(
            self.history_years_changed.emit
        )

        self.time_decay_spin_box.valueChanged.connect(
            self.time_decay_changed.emit
        )

        self.training_scope_combo_box.currentIndexChanged.connect(
            self._emit_training_scope_changed
        )

        self.form_match_count_spin_box.valueChanged.connect(
            self.form_match_count_changed.emit
        )

        self.form_weight_spin_box.valueChanged.connect(
            self.form_weight_changed.emit
        )

        self.h2h_match_count_spin_box.valueChanged.connect(
            self.h2h_match_count_changed.emit
        )

        self.h2h_weight_spin_box.valueChanged.connect(
            self.h2h_weight_changed.emit
        )

        self.rho_mode_combo_box.currentIndexChanged.connect(
            self._emit_rho_mode_changed
        )

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def _create_ingress_widget(self):
        widget = QWidget()

        layout = self.create_vertical_layout(parent=widget)

        label = QLabel(
            "<i>"
            "Här kan du konfigurera programmets utseende och funktioner. "
            "Alla inställningar sparas automatiskt."
            "</i>"
        )

        label.setWordWrap(True)
        label.setAlignment(self.INGRESS_ALIGNMENT)
        layout.addWidget(label)

        self.layout.addWidget(widget)

    def _create_form_widget(self):
        container = QWidget()
        layout = QFormLayout(container)

        self.font_combo_box = BaseComboBox()

        self.history_years_spin_box = QSpinBox()
        self.history_years_spin_box.setRange(1, 10)
        self.history_years_spin_box.setSuffix(" år")

        self.time_decay_spin_box = QDoubleSpinBox()
        self.time_decay_spin_box.setDecimals(4)
        self.time_decay_spin_box.setRange(0.0, 0.1)
        self.time_decay_spin_box.setSingleStep(0.0001)

        self.training_scope_combo_box = BaseComboBox()
        self.training_scope_combo_box.addItem(
            "Hela landet",
            self.TRAINING_SCOPE_COUNTRY
        )
        self.training_scope_combo_box.addItem(
            "Endast tävlingen",
            self.TRAINING_SCOPE_COMPETITION
        )

        self.form_match_count_spin_box = QSpinBox()
        self.form_match_count_spin_box.setRange(1, 20)

        self.form_weight_spin_box = QDoubleSpinBox()
        self.form_weight_spin_box.setDecimals(2)
        self.form_weight_spin_box.setRange(0.0, 1.0)
        self.form_weight_spin_box.setSingleStep(0.01)

        self.h2h_match_count_spin_box = QSpinBox()
        self.h2h_match_count_spin_box.setRange(1, 20)

        self.h2h_weight_spin_box = QDoubleSpinBox()
        self.h2h_weight_spin_box.setDecimals(2)
        self.h2h_weight_spin_box.setRange(0.0, 1.0)
        self.h2h_weight_spin_box.setSingleStep(0.01)

        self.rho_mode_combo_box = BaseComboBox()
        self.rho_mode_combo_box.addItem(
            "Fast",
            self.RHO_MODE_FIXED
        )
        self.rho_mode_combo_box.addItem(
            "Skattad",
            self.RHO_MODE_ESTIMATED
        )

        layout.addRow(
            QLabel(self.FONT_LABEL),
            self.font_combo_box
        )

        layout.addRow(
            QLabel(self.HISTORY_YEARS_LABEL),
            self.history_years_spin_box
        )

        layout.addRow(
            QLabel(self.TIME_DECAY_LABEL),
            self.time_decay_spin_box
        )

        layout.addRow(
            QLabel(self.TRAINING_SCOPE_LABEL),
            self.training_scope_combo_box
        )

        layout.addRow(
            QLabel(self.FORM_MATCH_COUNT_LABEL),
            self.form_match_count_spin_box
        )

        layout.addRow(
            QLabel(self.FORM_WEIGHT_LABEL),
            self.form_weight_spin_box
        )

        layout.addRow(
            QLabel(self.H2H_MATCH_COUNT_LABEL),
            self.h2h_match_count_spin_box
        )

        layout.addRow(
            QLabel(self.H2H_WEIGHT_LABEL),
            self.h2h_weight_spin_box
        )

        layout.addRow(
            QLabel(self.RHO_MODE_LABEL),
            self.rho_mode_combo_box
        )

        self.layout.addWidget(container)

    # --------------------------------------------------
    # Typsnitt
    # --------------------------------------------------

    def update_font_combo_box(self, fonts=None):
        """
            Uppdaterar listan med tillgängliga typsnitt.
        """
        if fonts is None:
            fonts = []

        self.font_combo_box.blockSignals(True)

        self.font_combo_box.clear()
        self.font_combo_box.addItems(fonts)

        self.font_combo_box.blockSignals(False)

    def set_selected_font(self, font):
        """
            Väljer angivet typsnitt i comboboxen.
        """
        self.font_combo_box.blockSignals(True)

        index = self.font_combo_box.findText(font)

        if index >= 0:
            self.font_combo_box.setCurrentIndex(index)

        self.font_combo_box.blockSignals(False)

    def apply_font(
        self,
        font
    ):
        """
            Applicerar typsnittet på inställningsvyn.
        """
        self.setFont(font)

        for widget in self.findChildren(QWidget):
            widget.setFont(font)

        self.update()

    # --------------------------------------------------
    # Analysinställningar
    # --------------------------------------------------

    def set_history_years(self, value):
        self._set_spin_box_value(self.history_years_spin_box, value)

    def set_time_decay(self, value):
        self._set_spin_box_value(self.time_decay_spin_box, value)

    def set_form_match_count(self, value):
        self._set_spin_box_value(self.form_match_count_spin_box, value)

    def set_form_weight(self, value):
        self._set_spin_box_value(self.form_weight_spin_box, value)

    def set_h2h_match_count(self, value):
        self._set_spin_box_value(self.h2h_match_count_spin_box, value)

    def set_h2h_weight(self, value):
        self._set_spin_box_value(self.h2h_weight_spin_box, value)

    def set_training_scope(self, value):
        self._set_combo_box_data(self.training_scope_combo_box, value)

    def set_rho_mode(self, value):
        self._set_combo_box_data(self.rho_mode_combo_box, value)

    @staticmethod
    def _set_spin_box_value(spin_box, value):
        spin_box.blockSignals(True)
        spin_box.setValue(value)
        spin_box.blockSignals(False)

    @staticmethod
    def _set_combo_box_data(combo_box, value):
        combo_box.blockSignals(True)

        index = combo_box.findData(value)

        if index >= 0:
            combo_box.setCurrentIndex(index)

        combo_box.blockSignals(False)

    # --------------------------------------------------
    # Emitters
    # --------------------------------------------------

    def _emit_training_scope_changed(self):
        self.training_scope_changed.emit(
            self.training_scope_combo_box.currentData()
        )

    def _emit_rho_mode_changed(self):
        self.rho_mode_changed.emit(
            self.rho_mode_combo_box.currentData()
        )
