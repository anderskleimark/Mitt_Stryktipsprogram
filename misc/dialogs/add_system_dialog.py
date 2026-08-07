from PySide6.QtWidgets import (QComboBox, QFormLayout, QHBoxLayout, QLabel,
                               QMessageBox, QPushButton, QSpinBox, QVBoxLayout)

from misc.dialogs.base_dialog import BaseDialog


class AddSystemDialog(BaseDialog):
    """
        Dialog för att lägga till eller redigera ett tipssystem.
    """

    def __init__(
        self,
        system=None,
        parent=None
    ):
        """
            Initierar dialogen.

            Om ett System-objekt anges öppnas dialogen i
            redigeringsläge, annars i lägg-till-läge.
        """
        super().__init__(parent)

        self.system = system

        self._build_dialog()

        self.save_button.clicked.connect(
            self._on_save_clicked
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.type_combo.currentTextChanged.connect(
            self._on_type_changed
        )

        if self.system is not None:
            self.type_combo.setCurrentText(
                self.system.system_type
            )

            self.full_spin.setValue(
                self.system.full_covers
            )

            self.half_spin.setValue(
                self.system.half_covers
            )

            self.rows_spin.setValue(
                self.system.row_count
            )

        self._on_type_changed(
            self.type_combo.currentText()
        )

    def _build_dialog(self):
        """
            Bygger dialogens användargränssnitt.
        """
        self.setModal(True)

        self.type_combo = QComboBox()
        self.type_combo.addItems(
            ["M", "R", "U"]
        )

        self.full_spin = QSpinBox()
        self.full_spin.setRange(0, 13)

        self.half_spin = QSpinBox()
        self.half_spin.setRange(0, 13)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(
            1,
            500000
        )

        self.rows_label = QLabel(
            "Antal rader:"
        )

        form = QFormLayout()
        form.addRow(
            "Typ:",
            self.type_combo
        )

        form.addRow(
            "Helgarderingar:",
            self.full_spin
        )

        form.addRow(
            "Halvgarderingar:",
            self.half_spin
        )

        form.addRow(
            self.rows_label,
            self.rows_spin
        )

        self.save_button = QPushButton(
            "Spara"
        )

        self.cancel_button = QPushButton(
            "Avbryt"
        )

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(
            self.save_button
        )
        buttons.addWidget(
            self.cancel_button
        )

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addSpacing(15)
        layout.addLayout(buttons)

        self.setLayout(layout)

        if self.system is None:
            self.setWindowTitle(
                "Lägg till tipssystem"
            )
        else:
            self.setWindowTitle(
                "Redigera tipssystem"
            )

    def _on_type_changed(
        self,
        system_type
    ):
        """
            Visar eller döljer fältet för antal rader
            beroende på vald systemtyp.
        """
        mathematical = (
            system_type == "M"
        )

        self.rows_label.setVisible(
            not mathematical
        )

        self.rows_spin.setVisible(
            not mathematical
        )

    def _on_save_clicked(self):
        """
            Sparar dialogens innehåll om
            valideringen lyckas.
        """
        if not self._validate():
            return

        self.accept()

    def _validate(self):
        """
            Validerar användarens inmatning.

            Returnerar True om all information
            är giltig.
        """
        full = self.full_spin.value()
        half = self.half_spin.value()

        if full + half > 13:
            QMessageBox.warning(
                self,
                "Fel",
                "Antalet helgarderingar och "
                "halvgarderingar får tillsammans "
                "inte överstiga 13."
            )
            return False

        if full == 0 and half == 0:
            QMessageBox.warning(
                self,
                "Fel",
                "Minst en gardering måste anges."
            )
            return False

        return True

    @property
    def system_type(self):
        """
            Returnerar vald systemtyp.
        """
        return self.type_combo.currentText()

    @property
    def full_covers(self):
        """
            Returnerar antal helgarderingar.
        """
        return self.full_spin.value()

    @property
    def half_covers(self):
        """
            Returnerar antal halvgarderingar.
        """
        return self.half_spin.value()

    @property
    def row_count(self):
        """
            Returnerar antal rader.

            För matematiska system beräknas
            antalet automatiskt.
        """
        if self.system_type == "M":
            return (
                3 ** self.full_covers
            ) * (
                2 ** self.half_covers
            )

        return self.rows_spin.value()
