from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from widgets.base_widget import BaseWidget


class OddsAnalysisWidget(BaseWidget):
    """
        Widget för att visa oddsanalys.

        Widgeten är förberedd för framtida
        oddsberäkningar och visar tills vidare
        endast en rubrik.
    """

    # --------------------------------------------------
    # Texter
    # --------------------------------------------------

    LABEL_ODDS = "Oddsanalys"

    def __init__(self):
        """
            Initierar oddsanalyswidgeten.
        """
        super().__init__()

        self.create_widgets()
        self.create_layout()

    # --------------------------------------------------
    # Uppbyggnad
    # --------------------------------------------------

    def create_widgets(self):
        """
            Skapar widgetens innehåll.
        """
        self.odds_label = QLabel(self.LABEL_ODDS)
        self.odds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def create_layout(self):
        """
            Skapar widgetens layout.
        """
        layout = self.create_vertical_layout(
            parent=self,
            spacing=None
        )

        layout.addWidget(self.odds_label)

    # --------------------------------------------------
    # Visa analys
    # --------------------------------------------------

    def show_analysis(
        self,
        analysis
    ):
        """
            Visar oddsanalysen.

            Metoden är förberedd för framtida
            oddsberäkningar.
        """
        pass

    # --------------------------------------------------
    # Tillstånd
    # --------------------------------------------------

    def clear_analysis(self):
        """
            Återställer oddsanalysen.

            Metoden är förberedd för framtida
            oddsberäkningar.
        """
        pass
