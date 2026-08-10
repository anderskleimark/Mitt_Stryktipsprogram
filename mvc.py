import locale

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel,
                               QVBoxLayout, QWidget)

from widgets.base_widget import BaseWidget


class Model:
    """
        Basklass för modeller.
        Innehåller gemensamma hjälpfunktioner för modeller.
    """

    @staticmethod
    def sort_by_keys(items, *attributes, reverse=False):
        """
            Sorterar objekt efter angivna attribut.
            Den kan sortera efter flera attribut i prioriteringsordning.
        """
        items.sort(
            key=lambda item: tuple(
                locale.strxfrm(str(getattr(item, attr)))
                for attr in attributes
            ),
            reverse=reverse
        )

        return items


class View(BaseWidget):
    """
        Basklass för vyer.
        Innehåller gemensamma funktioner för layout,
        rubriker, marginaler och dialogrutor.
    """
    # Standardmarginaler för huvudlayout.
    LEFT_MARGIN = 50
    RIGHT_MARGIN = 50
    TOP_MARGIN = 50
    BOTTOM_MARGIN = 50

    # Layoutinställningar.
    HEADER_BOTTOM_MARGIN = 10

    def __init__(self):
        super().__init__()
        self.header = None
        self.header_font = QFont("Arial", 18, QFont.Bold)
        self._selection_tables = set()
        self.installEventFilter(self)

    def get_active_selection_table(self):
        """
            Returnerar aktiv tabell.
        """

    def create_layout(self):
        """
            Skapar huvudlayout.
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(
            self.LEFT_MARGIN,
            self.TOP_MARGIN,
            self.RIGHT_MARGIN,
            self.BOTTOM_MARGIN
        )
        return layout

    def create_header(self, text):
        """
            Skapar en standardrubrik.
        """
        self.header = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, self.HEADER_BOTTOM_MARGIN)

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
        """
            Uppdaterar rubriktext och flagga.
        """
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

    def eventFilter(self, obj, event):
        """
            Hanterar klick utanför tabeller.
        """
        if event.type() == QEvent.Type.MouseButtonPress:
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


class Controller:
    """
        Basklass för controllers.
    """

    def __init__(self, view):
        self.view = view

    def add_connections(self):
        """
            Kopplar signaler.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} måste implementera add_connections()"
        )

    def on_show_view(self):
        """
            Anropas precis innan controllerns vy visas.
        """
