from mvc import Model


class SettingModel(Model):
    """
        Modell som används för att hämta och spara
        programmets inställningar.
    """

    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_setting(self, key):
        """
            Hämtar en inställning.
        """

        return self.database.setting_repository.get_setting(key)

    def set_setting(self, key, value):
        """
            Sparar eller uppdaterar en inställning.
        """
        self.database.setting_repository.set_setting(key, value)
