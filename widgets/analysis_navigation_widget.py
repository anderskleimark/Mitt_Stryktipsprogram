from PySide6.QtCore import Signal

from misc.buttons import (DixonColesButton, OddsButton, ProbabilityButton,
                          StatisticButton)
from widgets.base_widget import BaseWidget


class AnalysisNavigationWidget(BaseWidget):
    """
        Widget för navigering mellan analysvyerna.
    """

    statistics_clicked = Signal()
    dixon_coles_clicked = Signal()
    probability_clicked = Signal()
    odds_clicked = Signal()

    def __init__(self, parent=None):
        """
            Initierar widgeten.
        """
        super().__init__(parent)

        self.statistics_button = StatisticButton()
        self.dixon_coles_button = DixonColesButton()
        self.probability_button = ProbabilityButton()
        self.odds_button = OddsButton()

        self._create_layout()
        self._setup_signals()

    def _create_layout(self):
        """
            Skapar widgetens layout.
        """
        layout = self.create_horizontal_layout(parent=self)

        layout.addWidget(self.statistics_button)
        layout.addWidget(self.dixon_coles_button)
        layout.addWidget(self.probability_button)
        layout.addWidget(self.odds_button)

    def _setup_signals(self):
        """
            Kopplar navigeringsknapparna till widgetens egna signaler.
        """
        self.statistics_button.clicked.connect(
            self.statistics_clicked.emit
        )

        self.dixon_coles_button.clicked.connect(
            self.dixon_coles_clicked.emit
        )

        self.probability_button.clicked.connect(
            self.probability_clicked.emit
        )

        self.odds_button.clicked.connect(
            self.odds_clicked.emit
        )

    def set_enabled(
        self,
        status
    ):
        """
            Aktiverar eller inaktiverar
            samtliga navigeringsknappar.
        """
        self.statistics_button.setEnabled(status)
        self.dixon_coles_button.setEnabled(status)
        self.probability_button.setEnabled(status)
        self.odds_button.setEnabled(status)
