from dataclasses import dataclass

from mvc import Model

# Klass för att hantera tipssystem.


@dataclass
class System:
    id: int
    system_type: str
    full_covers: int
    half_covers: int
    rows: int

    @property
    def type_name(self):

        return {
            "M": "M-system",
            "R": "R-system",
            "U": "U-system"
        }.get(self.system_type, self.system_type)

    @property
    def display_name(self):

        return (
            f"{self.system_type} "
            f"{self.full_covers}-"
            f"{self.half_covers}-"
            f"{self.rows}"
        )

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

        return System(*row)

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
                    system_id,
                    system_type,
                    full_covers,
                    half_covers,
                    rows_count
                )
            )

        return systems

    # Funktion som raderar ett tipssystem från databasen.

    def delete(self, system_id):
        self.database.delete_system(system_id)
