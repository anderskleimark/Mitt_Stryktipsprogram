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

        normal_css = ""
        disabled_css = ""

        for key, value in self._style.items():

            if key.startswith("disabled-"):
                css_key = key.replace("disabled-", "")
                disabled_css += f"{css_key}: {value};\n"

            else:
                normal_css += f"{key}: {value};\n"

        stylesheet = f"""
            QPushButton {{
                {normal_css}
            }}
        """

        if disabled_css:
            stylesheet += f"""
                QPushButton:disabled {{
                    {disabled_css}
                }}
            """

        self.setStyleSheet(stylesheet)

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
        return Style.BUTTON.copy()


class EditButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Redigera", parent)

    def default_style(self):
        return Style.BUTTON.copy()


class DeleteButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Radera", parent)

    def default_style(self):
        return Style.DELETE_BUTTON.copy()


class BackButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Tillbaka", parent)

    def default_style(self):
        return Style.BUTTON.copy()


class ShowTableButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Visa tabell", parent)

    def default_style(self):
        return Style.BUTTON.copy()


class InfoButton(BaseButton):
    def __init__(self, parent=None):
        super().__init__("Visa information", parent)

    def default_style(self):
        return Style.BUTTON.copy()
