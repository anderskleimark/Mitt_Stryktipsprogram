from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)


class AddTeamDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Lägg till lag")

        self.team_name = None

        self.create_widgets()

    def create_widgets(self):

        layout = QVBoxLayout()

        # Lagnamn
        name_layout = QHBoxLayout()

        name_layout.addWidget(
            QLabel("Lagnamn:")
        )

        self.team_name_edit = QLineEdit()

        name_layout.addWidget(
            self.team_name_edit
        )

        layout.addLayout(
            name_layout
        )

        # Knappar
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton(
            "OK"
        )

        self.cancel_button = QPushButton(
            "Avbryt"
        )

        button_layout.addWidget(
            self.ok_button
        )

        button_layout.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            button_layout
        )

        self.setLayout(
            layout
        )

        self.ok_button.clicked.connect(
            self.accept
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

    def accept(self):

        name = self.team_name_edit.text().strip()

        if not name:
            return

        self.team_name = name

        super().accept()
