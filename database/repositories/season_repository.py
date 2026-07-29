from database.repositories.repository import Repository


class SeasonRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    # Funktion som skapar en ny säsong för en viss tävling/liga.

    def create_season(self, competition_id, start_year, end_year):
        try:
            self.cursor.execute("""
                INSERT INTO seasons(
                    competition_id,
                    start_year,
                    end_year
                )
                VALUES(?, ?, ?)
            """, (
                competition_id,
                start_year,
                end_year
            ))

            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError("Säsongen finns redan.")

    # Funktion som raderar en säsong med hjälp av dess id.
    def delete_season(self, season_id):
        self.cursor.execute("""
            DELETE FROM seasons
            WHERE id = ?
        """, (season_id,))

        self.connection.commit()

    # Funktion som hämtar och returnerar alla säsonger, som har lagt till i databasen.
    def get_all_seasons(self):
        self.cursor.execute("""
            SELECT
                seasons.id,
                competitions.id AS competition_id,
                competitions.competition_name,
                competitions.country_id,
                seasons.start_year,
                seasons.end_year
            FROM seasons
            JOIN competitions
                ON seasons.competition_id = competitions.id
            """)

        return self.cursor.fetchall()

    # Funktion som returnerar data om alla en tävling/ligas säsonger.
    def get_seasons(self, competition_id):
        self.cursor.execute("""
        SELECT
            seasons.id AS season_id,
            seasons.start_year,
            seasons.end_year,
            competitions.id AS competition_id,
            competitions.country,
            competitions.competition_name
        FROM seasons
        JOIN competitions
            ON seasons.competition_id = competitions.id
        WHERE competitions.id = ?
        ORDER BY seasons.start_year DESC
            """, (competition_id,))

        return self.cursor.fetchall()

    # Funktion som returnerar statistik om en tävling/liga för en viss säsong.
    def get_season_statistics(self, season_id):
        self.cursor.execute("""
            SELECT
                COUNT(*) AS matches_played,
                SUM(home_score) AS total_home_goals,
                SUM(away_score) AS total_away_goals
            FROM matches
            WHERE season_id = ?
            AND home_score IS NOT NULL
            AND away_score IS NOT NULL
        """, (season_id,))

        return self.cursor.fetchone()
