from dataclasses import dataclass

from PySide6.QtWidgets import (QDoubleSpinBox, QGridLayout, QLabel, QSpinBox,
                               QWidget)


@dataclass(frozen=True)
class RangeConfig:
    """
        Konfiguration för ett numeriskt intervall.
    """

    minimum_label: str
    maximum_label: str
    step_label: str

    minimum: float
    maximum: float

    default_minimum: float
    default_maximum: float
    default_step: float

    decimals: int | None = None
    single_step: float = 1
    integer: bool = False


class RangeSettingsWidget(QWidget):
    """
        Widget för ett intervall med
        minimum, maximum och steg.
    """

    def __init__(
        self,
        settings,
        parent=None
    ):
        """
            Initierar intervallwidgeten från
            angiven konfiguration.
        """
        super().__init__(parent)

        self.settings = settings

        self.minimum_spin_box = self._create_spin_box(
            minimum=settings.minimum,
            maximum=settings.maximum,
            decimals=settings.decimals,
            single_step=settings.single_step,
            integer=settings.integer
        )

        self.maximum_spin_box = self._create_spin_box(
            minimum=settings.minimum,
            maximum=settings.maximum,
            decimals=settings.decimals,
            single_step=settings.single_step,
            integer=settings.integer
        )

        self.step_spin_box = self._create_spin_box(
            minimum=settings.single_step,
            maximum=settings.maximum,
            decimals=settings.decimals,
            single_step=settings.single_step,
            integer=settings.integer
        )

        self.minimum_spin_box.setValue(
            settings.default_minimum
        )

        self.maximum_spin_box.setValue(
            settings.default_maximum
        )

        self.step_spin_box.setValue(
            settings.default_step
        )

        layout = QGridLayout(self)

        layout.addWidget(QLabel(settings.minimum_label), 0, 0)

        layout.addWidget(self.minimum_spin_box, 0, 1)

        layout.addWidget(
            QLabel(settings.maximum_label),
            1,
            0
        )

        layout.addWidget(self.maximum_spin_box, 1, 1)
        layout.addWidget(QLabel(settings.step_label), 2, 0)
        layout.addWidget(self.step_spin_box, 2, 1)

    @staticmethod
    def _create_spin_box(
        *,
        minimum,
        maximum,
        decimals,
        single_step,
        integer
    ):
        """
            Skapar en spin box för heltal eller decimaltal.
        """
        if integer:
            spin_box = QSpinBox()

        else:
            spin_box = QDoubleSpinBox()
            spin_box.setDecimals(decimals)

        spin_box.setRange(
            minimum,
            maximum
        )

        spin_box.setSingleStep(
            single_step
        )

        return spin_box

    def get_minimum(self):
        """
            Returnerar valt minimivärde.
        """
        return self.minimum_spin_box.value()

    def get_maximum(self):
        """
            Returnerar valt maximivärde.
        """
        return self.maximum_spin_box.value()

    def get_step(self):
        """
            Returnerar valt stegvärde.
        """
        return self.step_spin_box.value()

    def get_range(self):
        """
            Returnerar minimum, maximum och steg.
        """
        return (
            self.get_minimum(),
            self.get_maximum(),
            self.get_step()
        )

    def set_enabled(self, enabled):
        """
            Aktiverar eller inaktiverar samtliga fält.
        """
        self.minimum_spin_box.setEnabled(enabled)
        self.maximum_spin_box.setEnabled(enabled)
        self.step_spin_box.setEnabled(enabled)
