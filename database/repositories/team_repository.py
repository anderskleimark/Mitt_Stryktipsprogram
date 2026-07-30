from database.repositories.repository import Repository
from models.domains import Competition, Season, SoccerMatch, Team
import sqlite3


class TeamRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    def get_teams(self, country_id=None):
        query = """
            SELECT
                t.id AS team_id,
                t.country_id as team_country_id,
                t.team_name,
                t.display_name AS team_display_name,

                c.id AS country_id,
                c.country_name AS country_name,
                c.iso_code AS country_code

            FROM teams t

            JOIN countries c
                ON t.country_id = c.id
        """

        parameters = []

        if country_id is not None:
            query += """
            WHERE c.id = ?
            """
            parameters.append(country_id)

        query += """
            ORDER BY t.team_name
        """

        self.cursor.execute(query, parameters)

        rows = self.cursor.fetchall()

        teams = []

        for row in rows:
            team = self.create_team(row)
            teams.append(team)

        return teams

    # Funktion som skapar ett nytt lag.
    def add_team(self, country_id, team_name, display_name):
        try:
            self.cursor.execute("""
                INSERT INTO teams(
                country_id,
                team_name,
                display_name
            )
                VALUES(?, ?, ?)
            """, (
                country_id,
                team_name,
                display_name
            ))

            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                "Laget finns redan."
            )

    # Funktion som hämtar id för ett lag.
    def get_team_id(self, team_name):
        self.cursor.execute("""
            SELECT id
            FROM teams
            WHERE team_name = ?
        """, (
            team_name,
        ))

        row = self.cursor.fetchone()

        if row:
            return row["id"]

        return None

    # Funktion som hämtar alla lag som deltar i en viss säsong.
    def get_teams_in_season(self, season_id):
        self.cursor.execute("""
            SELECT
                t.id AS team_id,
                t.team_name,
                t.display_name AS team_display_name,

                c.id AS team_country_id,
                c.country_name AS team_country_name,
                c.iso_code AS team_country_code

            FROM season_teams st

            JOIN teams t
                ON st.team_id = t.id

            JOIN countries c
                ON t.country_id = c.id

            WHERE st.season_id = ?

            ORDER BY t.team_name
        """, (
            season_id,
        ))

        return [
            self.create_team(row)
            for row in self.cursor.fetchall()
        ]

    # Funktion som lägger till ett lag till en säsong med hjälp av säsongens id och lagets id.
    def add_team_to_season(self, season_id, team_id):
        self.cursor.execute("""
            INSERT OR IGNORE INTO season_teams(
                season_id,
                team_id
            )
            VALUES(?, ?)
        """, (
            season_id,
            team_id
        ))

        self.connection.commit()

    # Funktion som tar bort ett lag från en säsong med hjälp av säsongens id och lagets id.
    def remove_team_from_season(self, season_id, team_id):
        if self.team_has_matches_in_season(
            season_id,
            team_id
        ):
            raise ValueError(
                "Laget kan inte tas bort, eftersom det "
                "finns matcher registrerade."
            )

        self.cursor.execute("""
            DELETE FROM season_teams
            WHERE season_id = ?
            AND team_id = ?
        """, (
            season_id,
            team_id
        ))

        self.connection.commit()

    # Funktion som kontrollerar om ett lag deltar i en säsong.
    def team_exists_in_season(self, season_id, team_id):
        self.cursor.execute("""
            SELECT 1
            FROM season_teams
            WHERE season_id = ?
            AND team_id = ?
        """, (
            season_id,
            team_id
        ))

        return self.cursor.fetchone() is not None

    # Funktion som tar bort ett lag från en säsong med hjälp av säsongens id och lagets id.
    def remove_team_from_season(self, season_id, team_id):
        if self.team_has_matches_in_season(
            season_id,
            team_id
        ):
            raise ValueError(
                "Laget kan inte tas bort, eftersom det "
                "finns matcher registrerade."
            )

        self.cursor.execute("""
            DELETE FROM season_teams
            WHERE season_id = ?
            AND team_id = ?
        """, (
            season_id,
            team_id
        ))

        self.connection.commit()

    # Funktion som returnerar alla ett lags seriemather för angiven säsong.
    def get_team_matches(self, season_id, team_id, venue="all"):
        query = """
            SELECT
                m.id AS match_id,
                m.match_date,
                m.home_score,
                m.away_score,

                s.id AS season_id,
                s.start_year,
                s.end_year,

                c.id AS competition_id,
                c.name AS competition_name,

                cc.id AS competition_country_id,
                cc.country_name AS competition_country_name,
                cc.iso_code AS competition_country_code,

                ht.id AS home_team_id,
                ht.team_name AS home_team_name,
                ht.display_name AS home_team_display_name,

                at.id AS away_team_id,
                at.team_name AS away_team_name,
                at.display_name AS away_team_display_name

            FROM matches m

            JOIN seasons s
                ON m.season_id = s.id

            JOIN competitions c
                ON s.competition_id = c.id

            JOIN countries cc
                ON c.country_id = cc.id

            JOIN teams ht
                ON m.home_team_id = ht.id

            JOIN teams at
                ON m.away_team_id = at.id

            WHERE m.season_id = ?
        """

        parameters = [season_id]

        if venue == "home":
            query += """
                AND m.home_team_id = ?
            """
            parameters.append(team_id)

        elif venue == "away":
            query += """
                AND m.away_team_id = ?
            """
            parameters.append(team_id)

        else:
            query += """
                AND (
                    m.home_team_id = ?
                    OR
                    m.away_team_id = ?
                )
            """
            parameters.extend(
                [team_id, team_id]
            )

        query += """
            ORDER BY m.match_date
        """

        self.cursor.execute(query, parameters)

        return [
            self.create_match(row)
            for row in self.cursor.fetchall()
        ]
