from mvc import Model

# Klass som hanterar data om fotbollsligor.


class League:
    def __init__(self, id, name, country):
        self.id = id
        self.name = name
        self.country = country

# Klass som hanterar data om säsonger.


class Season:
    def __init__(self, id, league_id, start_year, end_year):
        self.id = id
        self.league_id = league_id
        self.start_year = start_year
        self.end_year = end_year

# Klass som hanterar data om lag.


class Team:
    def __init__(self, id, name):
        self.id = id
        self.name = name

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

    # Funktion som hämtar och returnerar alla säsonger för en viss liga med hjälp av dess id.
    def get_seasons(self, league_id):

        rows = self.database.get_seasons(league_id)

        return [
            Season(
                row[0],
                league_id,
                row[1],
                row[2]
            )
            for row in rows
        ]

    # Funktion för att hämta och returnera alla lag i en viss liga.
    def get_teams(self, league_id):

        rows = self.database.get_teams(league_id)

        return [
            Team(
                row[0],
                row[1]
            )
            for row in rows
        ]
