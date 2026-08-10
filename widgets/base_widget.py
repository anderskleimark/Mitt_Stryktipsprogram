from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

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

    SPACING = 10

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

    def create_vertical_sub_layout(
        self,
        *,
        parent=None,
        spacing=None
    ):
        """
            Skapar en vertikal sublayout.
        """
        layout = QVBoxLayout(parent)

        layout.setContentsMargins(
            self.VERTICAL_LAYOUT_LEFT_MARGIN,
            self.VERTICAL_LAYOUT_TOP_MARGIN,
            self.VERTICAL_LAYOUT_RIGHT_MARGIN,
            self.VERTICAL_LAYOUT_BOTTOM_MARGIN
        )

        if spacing is None:
            layout.setSpacing(
                self.SPACING
            )
        else:
            layout.setSpacing(
                spacing
            )

        layout.addSpacing(1)

        return layout

    def create_horizontal_sub_layout(
        self,
        *,
        parent=None,
        spacing=None
    ):
        """
            Skapar en horisontell sublayout.
        """
        layout = QHBoxLayout(parent)

        layout.setContentsMargins(
            self.HORIZONTAL_LAYOUT_LEFT_MARGIN,
            self.HORIZONTAL_LAYOUT_TOP_MARGIN,
            self.HORIZONTAL_LAYOUT_RIGHT_MARGIN,
            self.HORIZONTAL_LAYOUT_BOTTOM_MARGIN
        )

        if spacing is None:
            layout.setSpacing(
                self.SPACING
            )
        else:
            layout.setSpacing(
                spacing
            )

        layout.addSpacing(1)

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
