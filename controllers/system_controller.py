

from mvc import Controller


class SystemController(Controller):
    def __init__(
        self,
        *,
        system_model,
        view
    ):
        super().__init__(view)
        self.system_model = system_model
        self.add_connections()
        self.load_all_systems()

    def add_connections(self):
        self.view.add_system_button.clicked.connect(
            self.on_add_system
        )
        self.view.delete_button.clicked.connect(
            self.on_delete_clicked
        )

        self.view.system_table.selectionModel().selectionChanged.connect(
            self.on_system_selection_changed
        )

    def load_all_systems(self):
        systems = self.system_model.get_all()

        if not systems:
            self.view.delete_button.setEnabled(False)
            self.view.update_systems([])
            return

        self.view.delete_button.setEnabled(False)
        self.view.update_systems(systems)

    def on_system_selection_changed(self):

        row = self.view.system_table.get_selected_row()
        self.view.delete_button.setEnabled(row >= 0)

    def on_add_system(self):
        """
            Lägger till ett nytt system.
        """
        result = self.view.show_add_system_dialog()

        if result is None:
            return

        (
            system_type,
            full_covers,
            half_covers,
            row_count
        ) = result

        try:
            self.system_model.add_system(
                system_type=system_type,
                full_covers=full_covers,
                half_covers=half_covers,
                row_count=row_count
            )

            self.load_all_systems()

        except ValueError as error:
            self.view.show_warning(
                "Fel",
                str(error)
            )

    def on_delete_clicked(self):
        """
            Raderar valt system.
        """
        row = self.view.system_table.get_selected_row()

        if row < 0:
            return

        system_id_item = self.view.system_table.item(
            row,
            0
        )

        if system_id_item is None:
            return

        system_id = int(
            system_id_item.text()
        )

        if not self.view.ask_confirmation(
            "Radera system",
            "Är du säker på att du vill radera systemet?"
        ):
            return

        bet_count = self.system_model.get_bet_count(system_id)

        if bet_count > 0:
            self.view.show_warning(
                "Kan inte radera",
                (
                    f"Systemet används av {bet_count} sparade vad "
                    "och kan därför inte raderas."
                )
            )
            return

        self.system_model.delete(system_id)

        self.load_all_systems()
        self.view.delete_button.setEnabled(False)
