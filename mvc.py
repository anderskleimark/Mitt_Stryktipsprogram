import locale
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QLabel, QVBoxLayout,
                               QWidget)


class Model:  # pylint: disable=too-few-public-methods
    """Basklass för modeller."""

    @staticmethod
    def sort_by_keys(items, *attributes):
        items.sort(
            key=lambda item: tuple(
                locale.strxfrm(str(getattr(item, attr)))
                for attr in attributes
            )
        )
# Basklass för vyerna.


class View(QWidget):

    def __init__(self):
        super().__init__()
        self.header = None
        self.header_font = QFont("Arial", 18, QFont.Bold)
        self._selection_tables = set()
        self.installEventFilter(self)

    # Funktion som returnerar aktiv tabell. Funktionen behöver implementeras av vyerna, om
    # funktionalatieten behövs.
    def get_active_selection_table(self):
        pass

    # Funktion för att skapa en standardlayout.
    def create_layout(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 30, 20, 20)
        return layout

    # Funktion för att skapa en standardrubrik.
    def create_header(self, text):
        self.header = QLabel(text)
        self.header.setFont(self.header_font)
        self.header.setAlignment(Qt.AlignCenter)

    # Funktion för att hanterar klick utanför tabeller i vyer.
    def eventFilter(self, obj, event):  # pylint: disable=invalid-name

        if event.type() == QEvent.Type.MouseButtonPress:

            # pylint: disable=assignment-from-no-return
            table = self.get_active_selection_table()

            if table is not None:

                # pylint: disable=assignment-from-no-return
                widget = QApplication.widgetAt(event.globalPosition(
                ).toPoint())

                if widget is None or (
                    widget is not table and
                    not table.isAncestorOf(widget)
                ):
                    table.clearSelection()
                    table.setCurrentCell(-1, -1)

        return super().eventFilter(obj, event)

    # Funktion för att ändra texten i sidans rubrik.
    def update_header_text(self, header_text):
        self.header.setText(header_text)

# Basklass för kontrollklasser.


class Controller:  # pylint: disable=too-few-public-methods

    def __init__(self, model, view):
        self.model = model
        self.view = view

    # Funktion för att lägga till lyssnare.
    def add_connections(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} måste implementera add_connections()"
        )
