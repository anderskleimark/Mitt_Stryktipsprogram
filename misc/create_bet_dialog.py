from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout
)

# Klass som används för att skapa en dialogruta, där användaren kan lägga till ett vad.


class CreateBetDialog(QDialog):

    def __init__(self, coupons, systems, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Nytt spel")
        self.setModal(True)
        self.setMinimumWidth(400)

        self._coupons = coupons
        self._systems = systems

        self.create_widgets()
        self.populate_coupons()
        self.populate_systems()

    # Funktion som skapar de widgetar, som ingår i dialogrutan.
    def create_widgets(self):

        layout = QVBoxLayout()
        form = QFormLayout()

        #
        # Kupong
        #

        self.coupon_combo = QComboBox()
        form.addRow(
            "Tipskupong:",
            self.coupon_combo
        )

        #
        # System
        #

        self.system_combo = QComboBox()
        form.addRow(
            "System:",
            self.system_combo
        )

        #
        # Datum
        #

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        form.addRow(
            "Datum:",
            self.date_edit
        )

        layout.addLayout(form)

        # Knappar.
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    # Funktion som tar fram tillagda tipskuponger och lägger in dem i en QComboBox.
    def populate_coupons(self):

        self.coupon_combo.clear()
        for coupon in self._coupons:

            text = (
                f"{coupon.year} - "
                f"vecka {coupon.week}"
            )

            self.coupon_combo.addItem(
                text,
                coupon.id
            )

     # Funktion som tar fram tillagda tipssystem och lägger in dem i en QComboBox.
    def populate_systems(self):

        self.system_combo.clear()
        for system in self._systems:

            self.system_combo.addItem(
                system.display_name,
                system.id
            )

    @property
    def coupon_id(self):

        return self.coupon_combo.currentData()

    @property
    def system_id(self):

        return self.system_combo.currentData()

    @property
    def date(self):

        return self.date_edit.date().toString(
            "yyyy-MM-dd"
        )
