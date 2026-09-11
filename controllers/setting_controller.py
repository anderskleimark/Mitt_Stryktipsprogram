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
        self.load_analysis_settings()

    def add_connections(self):
        """
            Kopplar signaler från vyn till controllern.
        """
        self.view.font_changed.connect(self.on_selected_font_changed)

        self.view.history_years_changed.connect(
            self.on_history_years_changed
        )
        self.view.time_decay_changed.connect(
            self.on_time_decay_changed
        )
        self.view.training_scope_changed.connect(
            self.on_training_scope_changed
        )
        self.view.form_match_count_changed.connect(
            self.on_form_match_count_changed
        )
        self.view.form_weight_changed.connect(
            self.on_form_weight_changed
        )
        self.view.h2h_match_count_changed.connect(
            self.on_h2h_match_count_changed
        )
        self.view.h2h_weight_changed.connect(
            self.on_h2h_weight_changed
        )
        self.view.rho_mode_changed.connect(
            self.on_rho_mode_changed
        )

    # --------------------------------------------------
    # Analysinställningar
    # --------------------------------------------------

    def load_analysis_settings(self):
        """
            Hämtar sparade analysinställningar
            och visar dem i vyn.
        """
        model = self.setting_model

        self.view.set_history_years(
            model.get_int_setting(
                model.ANALYSIS_HISTORY_YEARS,
                model.DEFAULT_HISTORY_YEARS
            )
        )

        self.view.set_time_decay(
            model.get_float_setting(
                model.ANALYSIS_TIME_DECAY,
                model.DEFAULT_TIME_DECAY
            )
        )

        self.view.set_training_scope(
            model.get_choice_setting(
                model.ANALYSIS_TRAINING_SCOPE,
                model.DEFAULT_TRAINING_SCOPE,
                ("country", "competition")
            )
        )

        self.view.set_form_match_count(
            model.get_int_setting(
                model.ANALYSIS_FORM_MATCH_COUNT,
                model.DEFAULT_FORM_MATCH_COUNT
            )
        )

        self.view.set_form_weight(
            model.get_float_setting(
                model.ANALYSIS_FORM_WEIGHT,
                model.DEFAULT_FORM_WEIGHT
            )
        )

        self.view.set_h2h_match_count(
            model.get_int_setting(
                model.ANALYSIS_H2H_MATCH_COUNT,
                model.DEFAULT_H2H_MATCH_COUNT
            )
        )

        self.view.set_h2h_weight(
            model.get_float_setting(
                model.ANALYSIS_H2H_WEIGHT,
                model.DEFAULT_H2H_WEIGHT
            )
        )

        self.view.set_rho_mode(
            model.get_choice_setting(
                model.ANALYSIS_RHO_MODE,
                model.DEFAULT_RHO_MODE,
                ("fixed", "estimated")
            )
        )

    def on_history_years_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_HISTORY_YEARS,
            str(value)
        )

    def on_time_decay_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_TIME_DECAY,
            str(value)
        )

    def on_training_scope_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_TRAINING_SCOPE,
            value
        )

    def on_form_match_count_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_FORM_MATCH_COUNT,
            str(value)
        )

    def on_form_weight_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_FORM_WEIGHT,
            str(value)
        )

    def on_h2h_match_count_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_H2H_MATCH_COUNT,
            str(value)
        )

    def on_h2h_weight_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_H2H_WEIGHT,
            str(value)
        )

    def on_rho_mode_changed(self, value):
        self.setting_model.set_setting(
            self.setting_model.ANALYSIS_RHO_MODE,
            value
        )

    # --------------------------------------------------
    # Typsnitt
    # --------------------------------------------------

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

        selected_font = self.setting_model.get_setting(
            self.setting_model.FONT_FAMILY
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
            self.setting_model.FONT_FAMILY,
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
