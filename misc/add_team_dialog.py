from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout
)


class AddTeamDialog(QDialog):

    def __init__(self, countries, parent=None):
        super().__init__(parent)

        self.countries = countries

        self._build_dialog()
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)

    # Bygger dialogen.
    def _build_dialog(self):

        self.setWindowTitle("Lägg till lag")
        self.setModal(True)

        self.country_combo = QComboBox()

        for country in self.countries:
            self.country_combo.addItem(
                country.country_name,
                country.id
            )

        self.name_edit = QLineEdit()
        self.display_name_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Land:", self.country_combo)
        form.addRow("Lagnamn:", self.name_edit)
        form.addRow("Visningsnamn:", self.display_name_edit)

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

    # Körs när användaren trycker på Spara.
    def _on_save_clicked(self):

        if not self._validate():
            return

        self.accept()

    # Validerar inmatningen.
    def _validate(self):

        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fel",
                "Lagets namn måste anges."
            )
            return False

        if not self.display_name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fel",
                "Visningsnamn måste anges."
            )
            return False

        return True

    @property
    def country_id(self):
        return self.country_combo.currentData()

    @property
    def team_name(self):
        return self.name_edit.text().strip()

    @property
    def display_name(self):
        return self.display_name_edit.text().strip()
