from mvc import Model


class CreateOwnSystemModel(Model):
    GAMES = 13

    def __init__(self):
        super().__init__()

    def get_max_half_cover(self, full_cover):
        return self.GAMES - full_cover

    def get_max_full_cover(self, half_cover):
        return self.GAMES - half_cover

    def create_system(self, full_cover, half_cover, guarantee, rows):
        pass
