from mvc import View
from PySide6.QtWidgets import (
    QComboBox,
    QTableWidget,
    QVBoxLayout,
    QLabel
)


class TeamView(View):
    def __init__(self):
        super().__init__()

        self.layout = self.create_layout()
        self.create_header("Lag")
        self.layout.addWidget(self.header)

        self._create_top_form()
        self._create_team_table()

        self.setLayout(self.layout)

    def _create_top_form(self):
        pass

    def _create_team_table(self):
        pass
