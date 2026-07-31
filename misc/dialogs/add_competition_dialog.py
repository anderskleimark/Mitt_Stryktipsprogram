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


class AddCompetitionDialog(BaseDialog):
    """
    Dialog för att lägga till eller redigera en tävling/liga.
    """

    def __init__(
        self,
        countries,
        competition=None,
        parent=None
    ):
        """
        Initierar dialogen.

        Om ett Competition-objekt anges öppnas dialogen i
        redigeringsläge, annars i lägg-till-läge.
        """
        super().__init__(parent)

        self.countries = countries
        self.competition = competition

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

        self.competition_name_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Land:", self.country_combo)
        form.addRow("Liga:", self.competition_name_edit)

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

        if self.competition is not None:
            self.setWindowTitle("Redigera tävling")

            self.competition_name_edit.setText(
                self.competition.competition_name
            )

            self.country_combo.setCurrentIndex(
                self.country_combo.findData(
                    self.competition.country.id
                )
            )

        else:
            self.setWindowTitle(
                "Lägg till tävling"
            )

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
        if not self.competition_name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fel",
                "Tävlingens namn måste anges."
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
    def competition_name(self):
        """
        Returnerar tävlingens namn.
        """
        return self.competition_name_edit.text().strip()
