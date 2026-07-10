from mvc import Model

# Klass som hanterar data om tävlingar/ligor.


class Competition:
    def __init__(self, id, name, country):
        self.id = id
        self.name = name
        self.country = country

# Klass som hanterar data om säsonger.


class Season:
    def __init__(self, id, competition_id, start_year, end_year):
        self.id = id
        self.competition_id = competition_id
        self.start_year = start_year
        self.end_year = end_year

# Klass som hanterar data om lag.


class Team:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Klass (Model) som används för att hämta och hantera data om fotbollsligor.


class CompetitionModel(Model):
    def __init__(self, database):
        super().__init__()
        self.database = database

    # Funktion som hämtar och returnerar alla ligor i databasen.
    def get_all(self):

        rows = self.database.get_all_competitions()
        competitions = []

        for row in rows:

            competitions.append(
                Competition(
                    row[0],
                    row[1],
                    row[2]
                )
            )

        return competitions

    # Funktion för att skapa en ny tävling/liga.
    def create_competition(self, name, country):
        self.database.create_competition(name, country)

    # Funktion för att radera en tävling/liga.
    def delete(self, competition_id):
        self.database.delete_competition(competition_id)

    # Funktion som hämtar och returnerar alla säsonger för en viss tävling/liga med hjälp av dess id.
    def get_seasons(self, commpetition_id):

        rows = self.database.get_seasons(commpetition_id)

        return [
            Season(
                row[0],
                commpetition_id,
                row[1],
                row[2]
            )
            for row in rows
        ]

    # Funktion för att hämta och returnera alla lag i en viss liga.
    def get_teams(self, commpetition_id):

        rows = self.database.get_teams(commpetition_id)

        return [
            Team(
                row[0],
                row[1]
            )
            for row in rows
        ]
