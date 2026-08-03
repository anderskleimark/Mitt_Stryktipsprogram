from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout
)

from misc.dialogs.base_dialog import BaseDialog


class SelectTeamDialog(BaseDialog):
    """
        Dialog för att välja ett befintligt lag.
    """

    def __init__(self, teams, parent=None):
        """
            Initierar dialogen.
        """
        super().__init__(parent)

        self.teams = teams

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
        self.setWindowTitle("Välj lag")

        self.team_combo = QComboBox()

        for team in self.teams:
            self.team_combo.addItem(
                team.display_name,
                team.id
            )

        form = QFormLayout()
        form.addRow(
            "Lag:",
            self.team_combo
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

    def _on_save_clicked(self):
        """
            Sparar valt lag.
        """
        self.accept()

    @property
    def team_id(self):
        """
            Returnerar valt lags id.
        """
        return self.team_combo.currentData()
