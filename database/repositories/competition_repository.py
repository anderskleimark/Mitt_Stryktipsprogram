from database.repositories.repository import Repository


class CompetitionRepository(Repository):
    """
        Klass för hantering av tävlingar i databasen.
    """

    def __init__(self, database):
        """
            Initierar klassen.
        """
        super().__init__(database)

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

    def get_competition_by_season(self, season_id):
        """
            Hämtar tävlingen för en viss säsong.
        """
        self.cursor.execute(
            """
                SELECT competitions.id              AS competiton_id,
                    competitions.competition_name   AS competition_name,
                    countries.id                    AS country_id,
                    countries.country_name          AS country_name,
                    countries.iso_code              AS country_code
                FROM competitions
                JOIN seasons
                    ON competitions.id = seasons.competition_id
                JOIN countries
                    ON competitions.country_id = countries.id
                WHERE seasons.id = ?
                """,
            (season_id,)
        )

        rows = self.cursor.fetchone()
        competitons = []
        for row in rows:
            competition = self.factory.create_competition(row)
            competitons.append(competition)
        return competitons
