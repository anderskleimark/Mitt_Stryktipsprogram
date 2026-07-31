from PySide6.QtWidgets import QDialog


class BaseDialog(QDialog):
    """
        Basklass för programmets dialogfönster.
        Klassen hanterar gemensam funktionalitet, såsom standardstorlek
        och gränssnitt för att bygga dialogens innehåll.
    """
    DEFAULT_WIDTH = 300
    DEFAULT_HEIGHT = 200

    def __init__(
        self,
        parent=None,
        width=None,
        height=None
    ):
        """
            Initierar dialogen och anger dess storlek.
        """
        super().__init__(parent)
        if (width is None):
            width = self.DEFAULT_WIDTH
        if (height is None):
            height = self.DEFAULT_HEIGHT
        self.resize(width, height)

    def _build_dialog(self):
        """
            Bygger dialogens användargränssnitt.
            Ska implementeras av subklasser.
        """
        ...
