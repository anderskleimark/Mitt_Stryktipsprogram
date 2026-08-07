from models.domains import System
from mvc import Model


class SystemModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    def add_system(
        self,
        *,
        system_type,
        full_covers,
        half_covers,
        row_count
    ):

        self.database.system_repository.add_system(
            system_type=system_type,
            full_covers=full_covers,
            half_covers=half_covers,
            row_count=row_count
        )

    def get(self, system_id):
        return self.database.system_repository.get(system_id)

    def get_all(self):
        return self.database.system_repository.get_all_systems()

    def get_bet_count(self, system_id):
        return self.database.get_bet_count_for_system(system_id)

    def delete(self, system_id):
        self.database.system_repository.delete_system(system_id)
