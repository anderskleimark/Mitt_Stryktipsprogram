from database.repositories.repository import Repository


class CompetitionRepository(Repository):
    """
        Klass för hantering av tävlingar i databasen.
    """

    def get_all_competitions(self):
        """
            Hämtar alla tävlingar.
        """
        self.cursor.execute(
            """
                SELECT
                    c.id                AS competition_id,
                    c.competition_name  AS competition_name,
                    co.id               AS competition_country_id,
                    co.country_name     AS competition_country_name,
                    co.iso_code         AS competition_country_code
                FROM competitions c
                JOIN countries co
                    ON c.country_id = co.id                
            """
        )

        rows = self.cursor.fetchall()
        competitions = []
        for row in rows:
            competition = self.factory.create_competition(row)
            competitions.append(competition)

        return competitions

    def add_competition(self, name, country):
        """
            Lägger till en ny tävling.
        """
        self.cursor.execute(
            """
                INSERT INTO competitions(competition_name, country_id)
                VALUES (?, ?)
            """,
            (name, country)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def delete_competition(self, competition_id):
        """
            Tar bort en tävling.
        """
        self.cursor.execute(
            """
            DELETE FROM competitions
            WHERE id= ?
            """,
            (competition_id,)
        )

        self.connection.commit()
