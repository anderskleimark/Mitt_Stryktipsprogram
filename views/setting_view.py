from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from misc.combo_boxes.base_combo_box import BaseComboBox
from mvc import View


class SettingView(View):
    """
        Vy för att visa och hantera inställningar.
    """
    # --------------------------------------------------
    # Signaler
    # --------------------------------------------------

    # Skickas när användaren ändrar typsnitt.
    font_changed = Signal(str)

    VIEW_TITLE = "Inställningar"
    FONT_LABEL = "Typsnitt"
    INGRESS_ALIGNMENT = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop

    def __init__(self):
        super().__init__()

        self.layout = self.create_main_layout()
        self.font_combo_box = None

        self.create_header(self.VIEW_TITLE)
        self.layout.addWidget(self.header)
        self._create_ingress_widget()
        self._create_form_widget()

        self.setLayout(self.layout)

        # Koppla combo-boxen till signalen.
        self.font_combo_box.currentTextChanged.connect(
            self.emit_font_changed
        )

    def _create_ingress_widget(self):
        widget = QWidget()

        layout = self.create_vertical_layout(
            parent=widget,
            spacing=None
        )

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
        layout.addRow(
            QLabel(self.FONT_LABEL),
            self.font_combo_box
        )

        self.layout.addWidget(container)

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

    def emit_font_changed(self, font):
        """
            Skickar signal när användaren ändrar typsnitt.
        """
        self.font_changed.emit(font)
