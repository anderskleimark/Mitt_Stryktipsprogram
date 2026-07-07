from mvc import Controller, Model, View


class LeagueController(Controller):

    def __init__(self, model, view):
        super().__init__(model, view)
        self.add_connections()

    def add_connections(self):
        pass
