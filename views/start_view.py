from PySide6.QtCore import Qt
from mvc import Model, View, Controller
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel

# Klass för startvyn.


class StartView(View):
    def __init__(self):
        super().__init__()
        layout = self.create_layout()
        self.create_header("Välkommen till mitt stryktipsprogram")
        layout.addWidget(self.header)
        self.setLayout(layout)
