from mvc import Model


class SettingModel(Model):
    """
        Modell som används för att hämta och spara
        programmets inställningar.
    """

    FONT_FAMILY = "font_family"

    ANALYSIS_HISTORY_YEARS = "analysis_history_years"
    ANALYSIS_TIME_DECAY = "analysis_time_decay"
    ANALYSIS_TRAINING_SCOPE = "analysis_training_scope"

    ANALYSIS_FORM_MATCH_COUNT = "analysis_form_match_count"
    ANALYSIS_FORM_WEIGHT = "analysis_form_weight"

    ANALYSIS_H2H_MATCH_COUNT = "analysis_h2h_match_count"
    ANALYSIS_H2H_WEIGHT = "analysis_h2h_weight"

    ANALYSIS_RHO_MODE = "analysis_rho_mode"

    DEFAULT_HISTORY_YEARS = 3
    DEFAULT_TIME_DECAY = 0.0027
    DEFAULT_TRAINING_SCOPE = "country"

    DEFAULT_FORM_MATCH_COUNT = 5
    DEFAULT_FORM_WEIGHT = 0.0

    DEFAULT_H2H_MATCH_COUNT = 5
    DEFAULT_H2H_WEIGHT = 0.0

    DEFAULT_RHO_MODE = "fixed"

    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_setting(self, key, default=None):
        """
            Hämtar en inställning.

            Om inställningen saknas returneras default.
        """
        value = self.database.setting_repository.get_setting(key)

        if value is None:
            return default

        return value

    def get_int_setting(self, key, default):
        """
            Hämtar en heltalsinställning.
        """
        value = self.get_setting(key)

        if value is None:
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float_setting(self, key, default):
        """
            Hämtar en flyttalsinställning.
        """
        value = self.get_setting(key)

        if value is None:
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_choice_setting(self, key, default, valid_values):
        """
            Hämtar en textinställning som måste vara
            ett av de tillåtna värdena.
        """
        value = self.get_setting(key, default)

        if value not in valid_values:
            return default

        return value

    def set_setting(self, key, value):
        """
            Sparar eller uppdaterar en inställning.
        """
        self.database.setting_repository.set_setting(key, value)
