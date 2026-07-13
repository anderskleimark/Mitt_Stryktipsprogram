from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

# Klass som ärver QComboBox.


class BaseComboBox(QComboBox):  # pylint: disable=too-few-public-methods

    def __init__(self, scroll=False, center_alignment=True):

        super().__init__()
        self.scroll = scroll
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        if center_alignment:
            self.lineEdit().setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

    # pylint: disable=invalid-name
    def wheelEvent(self, event):

        if self.scroll:
            super().wheelEvent(event)
        else:
            event.ignore()
