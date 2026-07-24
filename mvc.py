import locale
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QLabel, QHBoxLayout, QVBoxLayout,
                               QWidget)
from PySide6.QtGui import QPixmap


class Model:  # pylint: disable=too-few-public-methods
    """Basklass för modeller."""

    @staticmethod
    def sort_by_keys(items, *attributes, reverse=False):
        items.sort(
            key=lambda item: tuple(
                locale.strxfrm(str(getattr(item, attr)))
                for attr in attributes
            ),
            reverse=reverse
        )

        return items
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
        self.header = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 10)

        self.header_flag = QLabel()
        self.header_flag.setFixedSize(30, 20)

        self.header_text = QLabel(text)

        self.header_text.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addStretch()

        layout.addWidget(self.header_flag)
        layout.addWidget(self.header_text)

        layout.addStretch()

        self.header.setLayout(layout)

    def update_header_text(self, text, flag_path=None):
        self.header_text.setText(text)

        if flag_path:
            pixmap = QPixmap(flag_path)
            self.header_flag.setPixmap(
                pixmap.scaled(
                    24,
                    16,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        else:
            self.header_flag.clear()

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


# Basklass för kontrollklasser.
class Controller:
    def __init__(self, view):
        self.view = view

    def add_connections(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} måste implementera add_connections()"
        )
