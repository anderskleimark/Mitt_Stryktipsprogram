from PySide6.QtWidgets import QPushButton
from misc.styles import Style


class BaseButton(QPushButton):
    """
        Abstrakt basklass för alla knappar i applikationen.

        Klassen innehåller gemensamma stilinställningar och funktioner
        för att hantera knappens utseende. Alla underklasser måste
        implementera default_style().
    """

    def __init__(self, text="", parent=None):
        """
            Initierar knappen och utför gemensamma inställningar.
        """
        super().__init__(text, parent)

        self._style = self.default_style().copy()
        self._update_style()

    def default_style(self):
        """
            Returnerar knappens standardstil.
        """
        raise NotImplementedError

    def _update_style(self):
        """
            Bygger och applicerar knappens stylesheet utifrån
            aktuella stilinställningar.
        """
        css = ""

        for key, value in self._style.items():
            css += f"{key}: {value};\n"

        self.setStyleSheet(f"""
            QPushButton {{
                {css}
            }}
        """)

    def set_style_value(self, key, value):
        """
            Uppdaterar en stilinställning och applicerar den direkt.
            key anger vilken CSS-egenskap som ska ändras och value
            anger det nya värdet.
        """
        self._style[key] = value
        self._update_style()


class AddButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Lägg till", parent)

    def default_style(self):
        return Style.BUTTON


class InfoButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Visa information", parent)

    def default_style(self):
        return Style.BUTTON


class DeleteButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Radera", parent)
        self.setProperty(
            "buttonClass",
            "warning"
        )

    def default_style(self):
        return Style.BUTTON
