from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox

)

# Klass för att skapa en dialog, där man kan lägga till ett nytt tipssystem.


class AddSystemDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.build_dialog()

        # Kopplingar
        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.on_type_changed(self.type_combo.currentText())

    # Skapar dialogen och dess innehåll.
    def build_dialog(self):
        self.setWindowTitle("Lägg till tipssystem")
        self.setModal(True)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["M", "R", "U"])

        self.full_spin = QSpinBox()
        self.full_spin.setRange(0, 13)

        self.half_spin = QSpinBox()
        self.half_spin.setRange(0, 13)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 500000)

        self.rows_label = QLabel("Antal rader:")

        form = QFormLayout()
        form.addRow("Typ:", self.type_combo)
        form.addRow("Helgarderingar:", self.full_spin)
        form.addRow("Halvgarderingar:", self.half_spin)
        form.addRow(self.rows_label, self.rows_spin)

        self.save_button = QPushButton("Spara")
        self.cancel_button = QPushButton("Avbryt")

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addSpacing(15)
        layout.addLayout(buttons)

        self.setLayout(layout)

    # Funktion som triggas, när användaren byter typ av tipssystem.
    def on_type_changed(self, system_type):

        mathematical = (system_type == "M")

        self.rows_label.setVisible(not mathematical)
        self.rows_spin.setVisible(not mathematical)

    # Funktion som triggas, när användare trycker på "spara".
    def on_save_clicked(self):

        full = self.full_spin.value()
        half = self.half_spin.value()

        if full + half > 13:
            QMessageBox.warning(
                self,
                "Fel",
                "Antalet helgarderingar och halvgarderingar får tillsammans inte överstiga 13."
            )
            return

        if full == 0 and half == 0:
            QMessageBox.warning(
                self,
                "Fel",
                "Minst en gardering måste anges."
            )
            return

        self.accept()

    @property
    def system_type(self):
        return self.type_combo.currentText()

    @property
    def full_covers(self):
        return self.full_spin.value()

    @property
    def half_covers(self):
        return self.half_spin.value()

    @property
    def rows(self):

        if self.system_type == "M":
            return (3 ** self.full_covers) * (2 ** self.half_covers)

        return self.rows_spin.value()
