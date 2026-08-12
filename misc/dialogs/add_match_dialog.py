from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QComboBox, QDateEdit, QGridLayout, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton, QSpinBox,
                               QVBoxLayout)

from misc.dialogs.base_dialog import BaseDialog


class AddMatchDialog(BaseDialog):
    """
        Dialog för att lägga till eller redigera en fotbollsmatch.
    """

    MINIMUM_SCORE = 0
    MAXIMUM_SCORE = 20

    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 500

    def __init__(
        self,
        current_team,
        teams,
        match=None,
        parent=None
    ):
        """
            Initierar dialogen.

            Om ett SoccerMatch-objekt anges öppnas dialogen
            i redigeringsläge.
        """
        super().__init__(
            parent,
            self.DEFAULT_WIDTH,
            self.DEFAULT_HEIGHT
        )

        self.current_team = current_team
        self.teams = teams
        self.match = match

        self._build_dialog()

        self.save_button.clicked.connect(
            self._on_save_clicked
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.home_away_combo.currentIndexChanged.connect(
            self.update_match_information
        )

        self.opponent_combo.currentIndexChanged.connect(
            self.update_match_information
        )

        self.update_match_information()

    def _build_dialog(self):
        """
            Bygger dialogens användargränssnitt.
        """

        self.setModal(True)

        self.setWindowTitle(
            "Redigera match"
            if self.match is not None
            else "Lägg till match"
        )

        layout = QVBoxLayout()

        # Matchtyp
        layout.addWidget(
            QLabel("Matchtyp")
        )

        self.home_away_combo = QComboBox()

        self.home_away_combo.addItems(
            [
                "Hemmaplan",
                "Bortaplan"
            ]
        )

        layout.addWidget(
            self.home_away_combo
        )

        # Motståndare
        layout.addWidget(
            QLabel("Motståndare")
        )

        self.opponent_combo = QComboBox()

        for team in self.teams:
            if team.id != self.current_team.id:
                self.opponent_combo.addItem(
                    team.team_name,
                    team.id
                )

        layout.addWidget(
            self.opponent_combo
        )

        # Matchinformation
        layout.addWidget(
            QLabel("Match")
        )

        match_layout = QGridLayout()

        match_layout.setHorizontalSpacing(10)
        match_layout.setVerticalSpacing(6)

        self.home_team_label = QLabel()
        self.home_team_label.setStyleSheet(
            "font-weight: bold;"
        )

        self.away_team_label = QLabel()
        self.away_team_label.setStyleSheet(
            "font-weight: bold;"
        )

        match_layout.addWidget(
            QLabel("Hemmalag:"),
            0,
            0
        )

        match_layout.addWidget(
            self.home_team_label,
            0,
            1
        )

        match_layout.addWidget(
            QLabel("Bortalag:"),
            1,
            0
        )

        match_layout.addWidget(
            self.away_team_label,
            1,
            1
        )

        layout.addLayout(
            match_layout
        )

        # Datum
        layout.addWidget(
            QLabel("Datum")
        )

        self.date_edit = QDateEdit()

        self.date_edit.setCalendarPopup(
            True
        )

        self.date_edit.setDate(
            QDate.currentDate()
        )

        layout.addWidget(
            self.date_edit
        )

        # Resultat
        layout.addWidget(
            QLabel("Resultat")
        )

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

        result_layout.addWidget(
            self.home_score_spin
        )

        result_layout.addWidget(
            QLabel("–")
        )

        result_layout.addWidget(
            self.away_score_spin
        )

        result_layout.addStretch()

        layout.addLayout(
            result_layout
        )

        # Knappar
        buttons = QHBoxLayout()

        buttons.addStretch()

        self.save_button = QPushButton(
            "Spara"
        )

        buttons.addWidget(
            self.save_button
        )

        self.cancel_button = QPushButton(
            "Avbryt"
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )

        # Redigeringsläge
        if self.match is not None:
            self._load_match()

    def _load_match(self):
        """
            Laddar information från befintlig match.
        """

        if self.match.home_team.id == self.current_team.id:
            self.home_away_combo.setCurrentIndex(0)
            opponent = self.match.away_team
        else:
            self.home_away_combo.setCurrentIndex(1)
            opponent = self.match.home_team

        index = self.opponent_combo.findData(
            opponent.id
        )

        if index >= 0:
            self.opponent_combo.setCurrentIndex(
                index
            )

        self.date_edit.setDate(
            QDate.fromString(
                str(self.match.match_date),
                "yyyy-MM-dd"
            )
        )

        self.home_score_spin.setValue(
            self.match.home_score
        )

        self.away_score_spin.setValue(
            self.match.away_score
        )

    def update_match_information(self):
        """
            Uppdaterar visning av hemma- och bortalag.
        """

        opponent = self.opponent_combo.currentText()

        if self.home:
            home_team = self.current_team.team_name
            away_team = opponent

        else:
            home_team = opponent
            away_team = self.current_team.team_name

        self.home_team_label.setText(
            home_team
        )

        self.away_team_label.setText(
            away_team
        )

    def _on_save_clicked(self):
        """
            Sparar matchen om valideringen lyckas.
        """

        if not self._validate():
            return

        self.accept()

    def _validate(self):
        """
            Validerar matchens information.
        """

        if self.opponent_id is None:
            QMessageBox.warning(
                self,
                "Fel",
                "Motståndare måste väljas."
            )

            return False

        return True

    @property
    def home(self):
        """
            Returnerar True om laget spelar hemma.
        """
        return self.home_away_combo.currentIndex() == 0

    @property
    def opponent_id(self):
        """
            Returnerar vald motståndares id.
        """
        return self.opponent_combo.currentData()

    @property
    def home_team_id(self):
        """
            Returnerar hemmalagets id.
        """
        if self.home:
            return self.current_team.id

        return self.opponent_id

    @property
    def away_team_id(self):
        """
            Returnerar bortalagets id.
        """
        if self.home:
            return self.opponent_id

        return self.current_team.id

    @property
    def match_date(self):
        """
            Returnerar matchdatum.
        """
        return self.date_edit.date().toString(
            "yyyy-MM-dd"
        )

    @property
    def home_score(self):
        """
            Returnerar hemmalagets mål.
        """
        return self.home_score_spin.value()

    @property
    def away_score(self):
        """
            Returnerar bortalagets mål.
        """
        return self.away_score_spin.value()
