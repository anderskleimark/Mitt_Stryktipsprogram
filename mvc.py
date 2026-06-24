from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class Model:

    def __init__(self):
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update(self)


class View(QWidget):

    def __init__(self):
        super().__init__()
        self.header_font = QFont("Arial", 18, QFont.Bold)

    def update(self, model):
        raise NotImplementedError(
            f"{self.__class__.__name__} måste implementera update()"
        )

    def create_layout(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 30, 20, 20)
        return layout

    def create_header(self, text):
        header = QLabel(text)
        header.setFont(self.header_font)
        header.setAlignment(Qt.AlignCenter)

        return header


class Controller:

    def __init__(self, model, view):
        self.model = model
        self.view = view
