from PySide6.QtCore import Qt
from mvc import Model, View, Controller
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel


class StartView(View):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        header = QLabel("Välkommen till mitt stryktipsprogram")
        header.setFont(self.header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        self.setLayout(layout)
