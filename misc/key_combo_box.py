from misc.base_combo_box import BaseComboBox

# Klass som ärver BaseComboBox. Tanken med klassen är att skapa combo-boxar,
# där användaren bara kan välja legala varianter av tipstecken
# i U-raden för de olika systemen.


class KeyComboBox(BaseComboBox):  # pylint: disable=too-few-public-methods

    def __init__(self, values=None):
        super().__init__()

        if values is None:
            values = [
                "",
                "1",
                "X",
                "2"]

        self.addItems(values)
