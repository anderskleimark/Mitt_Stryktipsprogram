from mvc import Model


class LeagueModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
