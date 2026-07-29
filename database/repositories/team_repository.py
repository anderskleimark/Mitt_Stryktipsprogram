from database.repositories.repository import Repository


class TeamRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    def get_all_teams(self):
        self.cursor.execute("""
            SELECT
            t.id,
            t.team_name,
            t.display_name,
            c.id   AS country_id,
            c.country_name AS country_name,
            c.iso_code AS country_code
        FROM teams t
        JOIN countries c
        ON t.country_id = c.id
        ORDER BY t.team_name            
        """)
        return self.cursor.fetchall()

    def get_teams_by_country(self, country_id):
        self.cursor.execute("""
            SELECT
            t.id,
            t.team_name,
            t.display_name,
            c.id   AS country_id,
            c.country_name AS country_name,
            c.iso_code AS country_code
        FROM teams t
        JOIN countries c
        ON t.country_id = c.id
        WHERE c.id = ?
        ORDER BY t.team_name

        """, (country_id))

        return self.cursor.execute()

    # Funktion som skapar ett nytt lag.
    def create_team(self, team_name):
        try:
            self.cursor.execute("""
                INSERT INTO teams(name)
                VALUES(?)
            """, (
                team_name,
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
            WHERE name = ?
        """, (
            team_name,
        ))

        row = self.cursor.fetchone()

        if row:
            return row["id"]

        return None

    # Funktion som hämtar alla lag som deltar i en viss säsong.

    def get_teams(self, season_id):
        self.cursor.execute("""
            SELECT
                t.id,
                t.name

            FROM season_teams st
            JOIN teams t
                ON st.team_id = t.id
            WHERE st.season_id = ?

        """, (season_id,))

        return self.cursor.fetchall()

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
            c.country,

            ht.id AS home_team_id,
            ht.name AS home_team_name,

            at.id AS away_team_id,
            at.name AS away_team_name

        FROM matches m

        JOIN seasons s
            ON m.season_id = s.id

        JOIN competitions c
            ON s.competition_id = c.id

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

        else:  # venue == "all"
            query += """
            AND (
                m.home_team_id = ?
                OR
                m.away_team_id = ?
            )
            """
            parameters.extend([team_id, team_id])

        query += """
        ORDER BY m.match_date
        """

        self.cursor.execute(query, parameters)

        return self.cursor.fetchall()
