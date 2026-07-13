from mvc import Controller


class CreateOwnSystemController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()

    def add_connections(self):
        self.view.full_cover_spin.valueChanged.connect(self.update_spin_limits)
        self.view.half_cover_spin.valueChanged.connect(self.update_spin_limits)
        self.view.create_system_button.clicked.connect(
            self.on_create_system_clicked)

    def update_spin_limits(self):
        full = self.view.full_cover_spin.value()
        half = self.view.half_cover_spin.value()

        self.view.full_cover_spin.blockSignals(True)
        self.view.half_cover_spin.blockSignals(True)

        self.view.half_cover_spin.setMaximum(
            self.model.get_max_half_cover(full))
        self.view.full_cover_spin.setMaximum(
            self.model.get_max_full_cover(half))

        self.view.full_cover_spin.blockSignals(False)
        self.view.half_cover_spin.blockSignals(False)

    def on_create_system_clicked(self):

        full = self.view.full_cover_spin.value()
        half = self.view.half_cover_spin.value()

        guarantee = int(self.view.min_guarantee_combo.currentText().split()[0])

        rows = int(self.view.rows_combo.currentText())

        system = self.model.create_system(full, half, guarantee, rows)
        self.view.show_system(system)
