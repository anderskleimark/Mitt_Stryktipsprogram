from database.repositories.country_repository import CountryRepository
from models.domains import Country
from mvc import Model


class CountryModel(Model):
    def __init__(self, database):
        """
            Initierar modellen med en databasanslutning.
        """
        super().__init__()
        self.database = database

    def get_all_countries(self):
        """
            Hämtar alla länder.
            Returnerar en lista med Country-objekt.
        """
        return self.database.country_repository.get_all_countries()
