from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout
)

from misc.dialogs.base_dialog import BaseDialog


class AddSeasonDialog(BaseDialog):
    """
        Dialog för att lägga till eller redigera en säsong.
    """

    MIN_YEAR = 1900
    MAX_YEAR = 2100

    def __init__(
        self,
        season=None,
        parent=None
    ):
        """
            Initierar dialogen.

        Om ett Season-objekt anges öppnas dialogen i
        redigeringsläge, annars i lägg-till-läge.
        """
        super().__init__(parent)

        self.season = season
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

        self.start_year_spinbox = QSpinBox()
        self.start_year_spinbox.setRange(
            self.MIN_YEAR,
            self.MAX_YEAR
        )

        self.end_year_spinbox = QSpinBox()
        self.end_year_spinbox.setRange(
            self.MIN_YEAR,
            self.MAX_YEAR
        )

        form = QFormLayout()
        form.addRow(
            "Startår:",
            self.start_year_spinbox
        )
        form.addRow(
            "Slutår:",
            self.end_year_spinbox
        )

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

        if self.season is not None:
            self.setWindowTitle("Redigera säsong")

            self.start_year_spinbox.setValue(
                self.season.start_year
            )

            self.end_year_spinbox.setValue(
                self.season.end_year
            )

        else:
            self.setWindowTitle("Lägg till säsong")

            self.start_year_spinbox.setValue(2025)
            self.end_year_spinbox.setValue(2026)

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
        if self.end_year < self.start_year:
            QMessageBox.warning(
                self,
                "Fel",
                "Slutåret måste vara större än eller lika med startåret."
            )
            return False

        return True

    @property
    def start_year(self):
        """
            Returnerar säsongens startår.
        """
        return self.start_year_spinbox.value()

    @property
    def end_year(self):
        """
            Returnerar säsongens slutår.
        """
        return self.end_year_spinbox.value()
