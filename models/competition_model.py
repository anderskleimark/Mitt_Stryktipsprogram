import locale

from mvc import Model

locale.setlocale(locale.LC_COLLATE, "sv_SE.UTF-8")


class CompetitionModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    def get_all(self):
        return self.database.competition_repository.get_all_competitions()

    def add_competition(self, name, country):
        self.database.competition_repository.add_competition(name, country)

    def delete(self, competition_id):
        self.database.competition_repository.delete_competition(competition_id)

    def add_season(self, competition_id, start_year, end_year):
        self.database.season_repository.add_season(
            competition_id, start_year, end_year)

    def delete_season(self, season_id):
        self.database.season_repository.delete_season(season_id)
