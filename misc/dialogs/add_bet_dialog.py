from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel,
                               QMessageBox, QPushButton, QVBoxLayout)

from misc.dialogs.base_dialog import BaseDialog


class AddBetDialog(BaseDialog):
    """
        Dialog för att lägga till ett nytt spel.
    """

    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 350

    def __init__(
        self,
        coupons,
        systems,
        parent=None
    ):
        """
            Initierar dialogen.
        """
        super().__init__(
            parent,
            self.DEFAULT_WIDTH,
            self.DEFAULT_HEIGHT
        )

        self.coupons = coupons
        self.systems = systems

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

        self.setWindowTitle(
            "Nytt spel"
        )

        layout = QVBoxLayout()

        #
        # Tipskupong
        #

        layout.addWidget(
            QLabel("Tipskupong")
        )

        self.coupon_combo = QComboBox()

        for coupon in self.coupons:

            text = (
                f"{coupon.coupon_year} - "
                f"vecka {coupon.coupon_week}"
            )

            self.coupon_combo.addItem(
                text,
                coupon.id
            )

        layout.addWidget(
            self.coupon_combo
        )

        #
        # System
        #

        layout.addWidget(
            QLabel("System")
        )

        self.system_combo = QComboBox()

        for system in self.systems:

            self.system_combo.addItem(
                system.display_name,
                system.id
            )

        layout.addWidget(
            self.system_combo
        )

        #
        # Datum
        #

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

        #
        # Knappar
        #

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

    def _on_save_clicked(self):
        """
            Sparar vadet om valideringen lyckas.
        """

        if not self._validate():
            return

        self.accept()

    def _validate(self):
        """
            Validerar vadets information.
        """

        if self.coupon_id is None:

            QMessageBox.warning(
                self,
                "Fel",
                "Tipskupong måste väljas."
            )

            return False

        if self.system_id is None:

            QMessageBox.warning(
                self,
                "Fel",
                "System måste väljas."
            )

            return False

        return True

    @property
    def coupon_id(self):
        """
            Returnerar vald tipskupongs id.
        """
        return self.coupon_combo.currentData()

    @property
    def system_id(self):
        """
            Returnerar valt systems id.
        """
        return self.system_combo.currentData()

    @property
    def date(self):
        """
            Returnerar vadets datum.
        """
        return self.date_edit.date().toString(
            "yyyy-MM-dd"
        )
