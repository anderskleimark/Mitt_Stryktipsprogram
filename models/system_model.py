from models.domains import System
from mvc import Model

# Modellklass för olika tipssystem.


class SystemModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion som lägger till ett tipssystem med hjälp av databasen.
    def create_system(
        self,
        system_type,
        full_covers,
        half_covers,
        rows
    ):

        self.database.create_system(
            system_type,
            full_covers,
            half_covers,
            rows
        )

    def get(self, system_id):
        row = self.database.get_system_row(system_id)

        if row is None:
            return None

        return System(
            id=row["id"],
            system_type=row["system_type"],
            full_covers=row["full_covers"],
            half_covers=row["half_covers"],
            rows=row["rows"]
        )

    # Funktion som returnerar alla tipssystem som har lagt in i databasen.

    def get_all(self):
        rows = self.database.get_all_systems()
        systems = []

        for (
            system_id,
            system_type,
            full_covers,
            half_covers,
            rows_count
        ) in rows:

            systems.append(
                System(
                    id=system_id,
                    system_type=system_type,
                    full_covers=full_covers,
                    half_covers=half_covers,
                    rows=rows_count
                )
            )

        return Model.sort_by_keys(systems, "full_covers", "half_covers", "rows", reverse=True)

    # Funktion som returnerar antal vad, som angivet tipssystem använder sig av.
    def get_bet_count(self, system_id):
        return self.database.get_bet_count_for_system(system_id)

    # Funktion som raderar ett tipssystem från databasen.
    def delete(self, system_id):
        self.database.delete_system(system_id)
