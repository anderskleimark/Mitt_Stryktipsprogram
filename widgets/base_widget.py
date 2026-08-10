from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QWidget

from misc.message_boxes import MessageBox


class BaseWidget(QWidget):
    """
        Basklass för widgetar.

        Innehåller gemensamma hjälpfunktioner
        för layout och dialogrutor.
    """

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    # Mellanrum
    SPACING = 10
    HORIZONTAL_GRID_SPACING = 10
    VERTICAL_GRID_SPACING = 4

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

    # Marginaler för grid-layouter.
    GRID_LAYOUT_LEFT_MARGIN = 0
    GRID_LAYOUT_RIGHT_MARGIN = 0
    GRID_LAYOUT_TOP_MARGIN = 0
    GRID_LAYOUT_BOTTOM_MARGIN = 0

    def create_vertical_layout(
        self,
        *,
        parent=None,
        spacing=None
    ):
        """
            Skapar en vertikal layout.
        """
        layout = QVBoxLayout(parent)

        layout.setContentsMargins(
            self.VERTICAL_LAYOUT_LEFT_MARGIN,
            self.VERTICAL_LAYOUT_TOP_MARGIN,
            self.VERTICAL_LAYOUT_RIGHT_MARGIN,
            self.VERTICAL_LAYOUT_BOTTOM_MARGIN
        )

        if spacing is None:
            layout.setSpacing(self.SPACING)
        else:
            layout.setSpacing(spacing)

        layout.addSpacing(1)
        return layout

    def create_horizontal_layout(
        self,
        *,
        parent=None,
        spacing=None
    ):
        """
            Skapar en horisontell layout.
        """
        layout = QHBoxLayout(parent)

        layout.setContentsMargins(
            self.HORIZONTAL_LAYOUT_LEFT_MARGIN,
            self.HORIZONTAL_LAYOUT_TOP_MARGIN,
            self.HORIZONTAL_LAYOUT_RIGHT_MARGIN,
            self.HORIZONTAL_LAYOUT_BOTTOM_MARGIN
        )

        if spacing is None:
            layout.setSpacing(self.SPACING)
        else:
            layout.setSpacing(spacing)

        layout.addSpacing(1)
        return layout

    def create_grid_layout(
        self,
        *,
        parent=None,
        horizontal_spacing=None,
        vertical_spacing=None
    ):
        """
            Skapar en grid-layout.
        """
        layout = QGridLayout(parent)

        layout.setContentsMargins(
            self.GRID_LAYOUT_LEFT_MARGIN,
            self.GRID_LAYOUT_TOP_MARGIN,
            self.GRID_LAYOUT_RIGHT_MARGIN,
            self.GRID_LAYOUT_BOTTOM_MARGIN
        )

        if horizontal_spacing is None:
            layout.setHorizontalSpacing(self.HORIZONTAL_GRID_SPACING)
        else:
            layout.setHorizontalSpacing(horizontal_spacing)

        if vertical_spacing is None:
            layout.setVerticalSpacing(self.VERTICAL_GRID_SPACING)
        else:
            layout.setVerticalSpacing(vertical_spacing)

        return layout

    # --------------------------------------------------
    # Dialogrutor
    # --------------------------------------------------

    def show_warning(self, title, message):
        """
            Visar ett varningsmeddelande.
        """
        MessageBox.warning(
            self,
            title,
            message
        )

    def show_information(self, title, message):
        """
            Visar ett informationsmeddelande.
        """
        MessageBox.information(
            self,
            title,
            message
        )

    def ask_question(self, title, message):
        """
            Visar ett meddelande där användaren
            kan välja mellan ja och nej.
        """
        return MessageBox.question(
            self,
            title,
            message
        )

    def ask_confirmation(self, title, message):
        """
            Visar ett meddelande där användaren
            kan välja mellan OK och avbryt.
        """
        return MessageBox.confirm(
            self,
            title,
            message
        )
