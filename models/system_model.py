from mvc import Model


class System:
    def __init__(
        self,
        system_id,
        system_type,
        full_covers,
        half_covers,
        rows
    ):
        self.id = system_id
        self.system_type = system_type
        self.full_covers = full_covers
        self.half_covers = half_covers
        self.rows = rows

    @property
    def type_name(self):

        return {
            "M": "M-system",
            "R": "R-system",
            "U": "U-system"
        }.get(self.system_type, self.system_type)


class SystemModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.systems = []

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

    # Funktion som returnerar alla tipssystem som har lagt in i databasen.
    def get_systems(self):
        rows = self.database.get_systems()

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

    def delete_system(self, system_id):
        self.database.delete_system(system_id)
