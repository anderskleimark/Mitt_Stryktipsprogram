from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class AddMatchDialog(QDialog):

    MINIMUM_SCORE = 0
    MAXIMUM_SCORE = 20
    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 500

    def __init__(self, current_team, teams, parent=None):
        super().__init__(parent)

        self.current_team = current_team

        self.setWindowTitle("Lägg till match")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        layout = QVBoxLayout()

        # Matchtyp
        layout.addWidget(QLabel("Matchtyp"))

        self.home_away_combo = QComboBox()
        self.home_away_combo.addItems([
            "Hemmaplan",
            "Bortaplan"
        ])

        layout.addWidget(self.home_away_combo)

        # Motståndare
        layout.addWidget(QLabel("Motståndare"))

        self.opponent_combo = QComboBox()

        for team in teams:
            self.opponent_combo.addItem(
                team.name,
                team.id
            )

        layout.addWidget(self.opponent_combo)

        # Match
        layout.addWidget(QLabel("Match"))

        match_layout = QGridLayout()
        match_layout.setHorizontalSpacing(10)
        match_layout.setVerticalSpacing(6)

        self.home_team_label = QLabel()
        self.home_team_label.setStyleSheet("font-weight: bold;")

        self.away_team_label = QLabel()
        self.away_team_label.setStyleSheet("font-weight: bold;")

        match_layout.addWidget(QLabel("Hemmalag:"), 0, 0)
        match_layout.addWidget(self.home_team_label, 0, 1)

        match_layout.addWidget(QLabel("Bortalag:"), 1, 0)
        match_layout.addWidget(self.away_team_label, 1, 1)

        layout.addLayout(match_layout)

        # Datum
        layout.addWidget(QLabel("Datum"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        layout.addWidget(self.date_edit)

        # Resultat
        layout.addWidget(QLabel("Resultat"))

        result_layout = QHBoxLayout()

        self.home_score_spin = QSpinBox()
        self.home_score_spin.setRange(
            self.MINIMUM_SCORE,
            self.MAXIMUM_SCORE
        )

        self.away_score_spin = QSpinBox()
        self.away_score_spin.setRange(
            self.MINIMUM_SCORE,
            self.MAXIMUM_SCORE
        )

        result_layout.addWidget(self.home_score_spin)
        result_layout.addWidget(QLabel("–"))
        result_layout.addWidget(self.away_score_spin)
        result_layout.addStretch()

        layout.addLayout(result_layout)

        # Knappar
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("Spara")
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Avbryt")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Signaler
        self.home_away_combo.currentIndexChanged.connect(
            self.update_match_information
        )

        self.opponent_combo.currentIndexChanged.connect(
            self.update_match_information
        )

        self.update_match_information()

    def update_match_information(self):

        opponent = self.opponent_combo.currentText()

        if self.home:
            home_team = self.current_team.name
            away_team = opponent
        else:
            home_team = opponent
            away_team = self.current_team.name

        self.home_team_label.setText(home_team)
        self.away_team_label.setText(away_team)

    @property
    def home(self):
        return self.home_away_combo.currentIndex() == 0

    @property
    def opponent_id(self):
        return self.opponent_combo.currentData()

    @property
    def match_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")

    @property
    def home_score(self):
        return self.home_score_spin.value()

    @property
    def away_score(self):
        return self.away_score_spin.value()
