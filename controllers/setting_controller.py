from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from mvc import Controller


class SettingController(Controller):
    """
        Controller för programmets inställningar.
    """

    def __init__(
        self,
        *,
        setting_model,
        view,
        main_window
    ):
        super().__init__(
            view
        )

        self.setting_model = setting_model
        self.main_window = main_window

        self.font_families = []

        self.add_connections()
        self.load_fonts()

    def add_connections(self):
        """
            Kopplar signaler från vyn till controllern.
        """
        self.view.font_changed.connect(self.on_selected_font_changed)

    def apply_font(self, font_family):
        """
            Aktiverar angivet typsnitt i programmet.
        """
        app = QApplication.instance()

        if app is not None:
            app.setFont(
                QFont(font_family)
            )

    def load_fonts(self):
        """
            Hämtar tillgängliga typsnitt och aktiverar
            det sparade typsnittet.
        """
        font_database = QFontDatabase()

        self.font_families.clear()

        for family in font_database.families():
            self.font_families.append(family)

        self.view.update_font_combo_box(
            self.font_families
        )

        selected_font = (
            self.setting_model.get_setting("font_family")
        )

        if selected_font:
            self.view.set_selected_font(selected_font)
            self.apply_font(selected_font)

    def on_selected_font_changed(
        self,
        font_family
    ):
        """
            Sparar och applicerar valt typsnitt.
        """
        self.setting_model.set_setting(
            "font_family",
            font_family
        )

        app = QApplication.instance()

        if app is None:
            return

        font = app.font()

        font.setFamily(
            font_family
        )

        app.setFont(font)

        self.main_window.apply_font(font)
        self.view.apply_font(font)
