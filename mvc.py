import locale
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QLabel, QHBoxLayout, QVBoxLayout,
                               QWidget)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox


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


class View(QWidget):
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

    # Marginaler för horisontella layouter.
    HORIZONTAL_LAYOUT_LEFT_MARGIN = 0
    HORIZONTAL_LAYOUT_RIGHT_MARGIN = 0
    HORIZONTAL_LAYOUT_TOP_MARGIN = 0
    HORIZONTAL_LAYOUT_BOTTOM_MARGIN = 0

    # Marginaler för vertikala layouter.
    VERTICAL_LAYOUT_LEFT_MARGIN = 0
    VERTICAL_LAYOUT_RIGHT_MARGIN = 0
    VERTICAL_LAYOUT_TOP_MARGIN = 0
    VERTICAL_LAYOUT_BOTTOM_MARGIN = 20

    # Layoutinställningar.
    HEADER_BOTTOM_MARGIN = 10
    SPACING = 10

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
        pass

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

    def create_vertical_sub_layout(self):
        """
            Skapar en vertikal sublayout.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(
            self.VERTICAL_LAYOUT_LEFT_MARGIN,
            self.VERTICAL_LAYOUT_TOP_MARGIN,
            self.VERTICAL_LAYOUT_RIGHT_MARGIN,
            self.VERTICAL_LAYOUT_BOTTOM_MARGIN
        )
        layout.setSpacing(self.SPACING)
        return layout

    def create_horizontal_sub_layout(self):
        """
            Skapar horisontell sublayout.
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(
            self.HORIZONTAL_LAYOUT_LEFT_MARGIN,
            self.HORIZONTAL_LAYOUT_TOP_MARGIN,
            self.HORIZONTAL_LAYOUT_RIGHT_MARGIN,
            self.HORIZONTAL_LAYOUT_BOTTOM_MARGIN
        )
        layout.setSpacing(self.SPACING)
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
        if event.type() == QEvent.Type.MouseButtonPress:
            """
                Hanterar klick utanför tabeller.
            """
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

    def show_warning(self, title, message):
        """
            Visar en dialogruta med ett varningsmeddelande.
        """
        QMessageBox.warning(
            self,
            title,
            message
        )


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

    def activate(self):
        """
            Aktiverar controller.
        """
        pass
