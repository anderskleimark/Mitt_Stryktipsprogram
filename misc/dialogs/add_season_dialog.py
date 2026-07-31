from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                               QSpinBox, QVBoxLayout)

# Klass för att visa en dialogruta för att kunna lägga till en säsong för en tävling/liga.


class AddSeasonDialog(QDialog):

    MIN_YEAR = 1900
    MAX_YEAR = 2100

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Lägg till säsong")

        self.start_year = None
        self.end_year = None

        self.create_widgets()

    def create_widgets(self):

        layout = QVBoxLayout()

        # Startår
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Startår:"))

        self.start_year_spinbox = QSpinBox()
        self.start_year_spinbox.setRange(
            self.MIN_YEAR,
            self.MAX_YEAR
        )
        self.start_year_spinbox.setValue(
            2025
        )

        start_layout.addWidget(
            self.start_year_spinbox
        )

        layout.addLayout(
            start_layout
        )

        # Slutår
        end_layout = QHBoxLayout()

        end_layout.addWidget(
            QLabel("Slutår:")
        )

        self.end_year_spinbox = QSpinBox()
        self.end_year_spinbox.setRange(
            self.MIN_YEAR,
            self.MAX_YEAR
        )
        self.end_year_spinbox.setValue(
            2026
        )

        end_layout.addWidget(
            self.end_year_spinbox
        )

        layout.addLayout(
            end_layout
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

        self.start_year = (
            self.start_year_spinbox.value()
        )

        self.end_year = (
            self.end_year_spinbox.value()
        )

        if self.end_year < self.start_year:
            return

        super().accept()
