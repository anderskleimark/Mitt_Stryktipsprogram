from mvc import Model

# Klass som hanterar data om fotbollsligor.


class League:
    def __init__(self, id, name, country):
        self.id = id
        self.name = name
        self.country = country

# Klass (Model) som används för att hämta och hantera data om fotbollsligor.


class LeagueModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion som hämtar och returnerar alla ligor i databasen.
    def get_all(self):

        rows = self.database.get_all_leagues()
        leagues = []

        for row in rows:

            leagues.append(
                League(
                    row[0],
                    row[1],
                    row[2]
                )
            )

        return leagues

    # Funktion för att skapa en ny liga.
    def create_league(self, name, country):
        self.database.create_league(name, country)

    # Funktion för att radera en liga.
    def delete(self, league_id):
        self.database.delete_league(league_id)
