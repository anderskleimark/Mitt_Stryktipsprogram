from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)


class AddLeagueDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.build_dialog()

        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.reject)

    def build_dialog(self):

        self.setWindowTitle("Lägg till liga")
        self.setModal(True)

        self.country_edit = QLineEdit()
        self.name_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Land:", self.country_edit)
        form.addRow("Liga:", self.name_edit)

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

    def on_save_clicked(self):

        if not self.country_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fel",
                "Land måste anges."
            )
            return

        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Fel",
                "Ligans namn måste anges."
            )
            return

        self.accept()

    @property
    def country(self):
        return self.country_edit.text().strip()

    @property
    def league_name(self):
        return self.name_edit.text().strip()
