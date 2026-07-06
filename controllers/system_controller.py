from mvc import Controller, Model, View
from misc.add_system_dialog import AddSystemDialog
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
)


class SystemController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()
        self.load_all_systems()

    def add_connections(self):
        self.view.add_system_button.clicked.connect(
            self.on_create_system
        )
        self.view.delete_button.clicked.connect(
            self.on_delete_clicked
        )

        self.view.system_table.selectionModel().selectionChanged.connect(
            self.on_system_selection_changed
        )

    # Funktion som hämtar tillaga tipssystem och skickar dem vidare till
    # vyn, som uppdaterar.
    def load_all_systems(self):
        systems = self.model.get_all()

        if not systems:
            self.view.delete_button.setEnabled(False)
            self.view.update_systems([])
            return

        self.view.delete_button.setEnabled(False)
        self.view.update_systems(systems)

    # Funktion som triggas, om användaren ändrar vald rad i systemtabellen.
    def on_system_selection_changed(self):

        row = self.view.system_table.get_selected_row()
        self.view.delete_button.setEnabled(row >= 0)

    # Funktion som öppnar en dialogruta för att skapa ett nytt tipssystem.
    def on_create_system(self):

        dialog = AddSystemDialog(self.view)

        if dialog.exec():
            try:
                self.model.create_system(
                    dialog.system_type,
                    dialog.full_covers,
                    dialog.half_covers,
                    dialog.rows
                )

                self.load_all_systems()

            except ValueError as e:

                QMessageBox.warning(
                    self.view,
                    "Fel",
                    str(e)
                )

    # Funktion som körs, om användare trycker på "Radera".
    def on_delete_clicked(self):
        row = self.system_table.get_selected_row()
        if row < 0:
            return

        system_id_item = self.view.system_table.item(row, 0)

        if system_id_item is None:
            return

        system_id = int(system_id_item.text())

        reply = QMessageBox.question(
            self.view,
            "Radera system",
            "Är du säker på att du vill radera systemet?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.model.delete(system_id)
        self.load_all_systems()
        self.view.delete_button.setEnabled(False)
