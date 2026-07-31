from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout
)
from misc.dialogs.base_dialog import BaseDialog


class AddTeamDialog(BaseDialog):
    """
        Dialog för att lägga till eller redigera ett lag.
    """

    def __init__(
        self,
        countries,
        team=None,
        parent=None
    ):
        """
            Initierar dialogen.
            Om ett Team-objekt anges öppnas dialogen i
            redigeringsläge, annars i lägg-till-läge.
        """
        super().__init__(parent)

        self.countries = countries
        self.team = team

        self._build_dialog()

        self.save_button.clicked.connect(
            self._on_save_clicked
        )
        self.cancel_button.clicked.connect(
            self.reject
        )

    def _build_dialog(self):
        """
            Bygger dialogens användargränssnitt.
        """
        self.setModal(True)
        self.country_combo = QComboBox()

        for country in self.countries:
            self.country_combo.addItem(
                country.country_name,
                country.id
            )

        self.team_name_edit = QLineEdit()
        self.display_name_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Land:", self.country_combo)
        form.addRow("Lagnamn:", self.team_name_edit)
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

        if self.team is not None:
            self.setWindowTitle("Redigera lag")

            self.team_name_edit.setText(
                self.team.team_name
            )

            self.display_name_edit.setText(
                self.team.display_name
            )

            self.country_combo.setCurrentIndex(
                self.country_combo.findData(
                    self.team.country.id
                )
            )
        else:
            self.setWindowTitle("Lägg till lag")

    def _on_save_clicked(self):
        """
            Sparar dialogens innehåll om valideringen lyckas.
        """
        if not self._validate():
            return

        self.accept()

    def _validate(self):
        """
            Validerar användarens inmatning.
            Returnerar True om all information är giltig.
        """
        if not self.team_name_edit.text().strip():
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
        """
            Returnerar id för valt land.
        """
        return self.country_combo.currentData()

    @property
    def team_name(self):
        """
            Returnerar lagets namn.
        """
        return self.team_name_edit.text().strip()

    @property
    def display_name(self):
        """
            Returnerar lagets visningsnamn.
        """
        return self.display_name_edit.text().strip()
