import sqlite3

from database.repositories.repository import Repository
from models.domains import SeasonStatistics


class SeasonRepository(Repository):
    """
        Klass för hantering av säsonger i databasen.
    """

    def add_season(self, competition_id, start_year, end_year):
        """
            Lägger till en ny säsong.
        """
        try:
            self.cursor.execute(
                """
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
                )
            )

            self.connection.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "Säsongen finns redan."
            ) from exc

    def delete_season(self, season_id):
        """
            Tar bort en säsong.
        """
        self.cursor.execute(
            """
                DELETE FROM seasons
                WHERE id = ?
            """,
            (season_id,)
        )

        self.connection.commit()

    def get_all_seasons(self):
        """
            Hämtar alla säsonger.
        """
        self.cursor.execute(
            """
                SELECT
                    seasons.id                      AS season_id,
                    seasons.start_year              AS season_start_year,
                    seasons.end_year                AS season_end_year,
                    competitions.id                 AS competition_id,
                    countries.id                    AS competition_country_id,
                    countries.country_name          AS competition_country_name,
                    countries.iso_code              AS competition_country_code,
                    competitions.competition_name   AS competition_name
                FROM seasons
                JOIN competitions
                    ON seasons.competition_id = competitions.id
                JOIN countries
                    ON countries.id = competitions.country_id
                ORDER BY seasons.start_year DESC
            """
        )

        rows = self.cursor.fetchall()
        seasons = []
        for row in rows:
            season = self.factory.create_season(row)
            seasons.append(season)

        return seasons

    def get_seasons(self, competition_id):
        """
            Hämtar alla säsonger för en viss tävling.
        """
        self.cursor.execute(
            """
                SELECT
                    seasons.id                      AS season_id,
                    seasons.start_year              AS season_start_year,
                    seasons.end_year                AS season_end_year,
                    competitions.id                 AS competition_id,
                    countries.id                    AS competition_country_id,
                    countries.country_name          AS competition_country_name,
                    countries.iso_code              AS competition_country_code,
                    competitions.competition_name   AS competition_name
                FROM seasons
                JOIN competitions
                    ON seasons.competition_id = competitions.id
                JOIN countries
                    ON countries.id = competitions.country_id
                WHERE competitions.id = ?
                ORDER BY seasons.start_year DESC
            """,
            (competition_id,)
        )
        rows = self.cursor.fetchall()
        seasons = []

        for row in rows:
            season = self.factory.create_season(row)
            seasons.append(season)

        return seasons

    def get(self, season_id):
        """
            Hämtar en säsong med hjälp av säsongens id.
        """
        self.cursor.execute(
            """
                SELECT
                    seasons.id                         AS season_id,
                    seasons.start_year                 AS season_start_year,
                    seasons.end_year                   AS season_end_year,
                    competitions.id                    AS competition_id,
                    competitions.competition_name      AS competition_name,
                    countries.id                       AS competition_country_id,
                    countries.country_name             AS competition_country_name,
                    countries.iso_code                 AS competition_country_code
                FROM seasons
                JOIN competitions
                    ON competitions.id = seasons.competition_id
                JOIN countries
                    ON countries.id = competitions.country_id
                WHERE seasons.id = ?
            """,
            (season_id,)
        )

        row = self.cursor.fetchone()
        if row:
            return self.factory.create_season(row)
        return None

    def get_season_statistics(self, season_id):
        """
            Hämtar statistik för en säsong.
        """
        self.cursor.execute(
            """
                SELECT
                    COUNT(*) AS matches_played,
                    SUM(home_score) AS total_home_goals,
                    SUM(away_score) AS total_away_goals
                FROM matches
                WHERE season_id = ?
                AND home_score IS NOT NULL
                AND away_score IS NOT NULL
            """,
            (season_id,)
        )
        row = self.cursor.fetchone()
        if row["matches_played"] is None:
            return None

        return SeasonStatistics(
            matches_played=row["matches_played"],
            total_home_goals=row["total_home_goals"],
            total_away_goals=row["total_away_goals"],
        )
