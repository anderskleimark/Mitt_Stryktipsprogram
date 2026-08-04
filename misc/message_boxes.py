from PySide6.QtWidgets import QMessageBox


class MessageBox:
    """
    Hjälpklass för att visa meddelanderutor.
    """

    @staticmethod
    def information(parent, title, message):
        """
        Visar ett informationsmeddelande.
        """
        QMessageBox.information(
            parent,
            title,
            message
        )

    @staticmethod
    def warning(parent, title, message):
        """
        Visar ett varningsmeddelande.
        """
        QMessageBox.warning(
            parent,
            title,
            message
        )

    @staticmethod
    def critical(parent, title, message):
        """
        Visar ett felmeddelande.
        """
        QMessageBox.critical(
            parent,
            title,
            message
        )

    @staticmethod
    def question(parent, title, message):
        """
        Visar en Ja/Nej-fråga.

        Returnerar:
            True  - användaren valde Ja.
            False - användaren valde Nej.
        """
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def confirm(parent, title, message):
        """
            Visar en Ok/Cancel-fråga.
            Returnerar:
                True  - användaren valde Ok.
                False - användaren valde Cancel.
            """
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(title)
        dialog.setText(message)

        dialog.setStandardButtons(
            QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel
        )

        dialog.setDefaultButton(
            QMessageBox.StandardButton.Cancel
        )

        return dialog.exec() == QMessageBox.StandardButton.Ok
