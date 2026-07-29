from database.repositories.repository import Repository


class CompetitionRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    # Funkton som hämtar och returnerar alla tävlingar/ligor.
    def get_all_competitions(self):
        self.cursor.execute("""
            SELECT id, competition_name, country_id
            FROM competitions
        """)

        return self.cursor.fetchall()

    # Funktion som skapar en ny liga i databasen.
    def create_competition(self, name, country):
        self.cursor.execute(
            """
            INSERT INTO competitions(name, country)
            VALUES (?, ?)
            """,
            (name, country)
        )
        self.connection.commit()

        return self.cursor.lastrowid

    # Funktion som raderar en liga med hjälp av ett id från databasen.
    def delete_competition(self, competition_id):
        self.cursor.execute("""
            DELETE FROM competitions
            WHERE id= ?
            """, (competition_id,))

        self.connection.commit()

    def get_competition_by_season(self, season_id):
        self.cursor.execute("""
            SELECT competitions.id AS id,
                competitions.name AS name,
                competitions.country AS country
            FROM competitions
            JOIN seasons
            ON competitions.id = seasons.competition_id
            WHERE seasons.id = ?
        """, (season_id,))

        return self.cursor.fetchone()
