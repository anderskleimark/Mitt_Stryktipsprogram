from database.repositories.repository import Repository


class MatchesRepository(Repository):
    """
        Klass som hanterar matcher i databasen.
    """

    def __init__(self, database):
        super().__init__(database)

    def get_matches_by_season(self, season_id):
        """
            Hämtar alla matcher för en säsong.
        """
        self.cursor.execute(
            """
                SELECT
                    m.home_team_id,
                    m.away_team_id,
                    m.home_score,
                    m.away_score
                FROM matches m
                WHERE m.season_id = ?
            """,
            (season_id,)
        )
        return self.cursor.fetchall()

    def add_match(
        self,
        *,
        season_id,
        home_team_id,
        away_team_id,
        match_date=None,
        home_score=None,
        away_score=None
    ):
        """
            Lägger till en ny match.
        """

        self.add_team_to_season(
            season_id,
            home_team_id
        )

        self.add_team_to_season(
            season_id,
            away_team_id
        )

        self.cursor.execute(
            """
                INSERT INTO matches(
                    season_id,
                    home_team_id,
                    away_team_id,
                    match_date,
                    home_score,
                    away_score
                )
                VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                season_id,
                home_team_id,
                away_team_id,
                match_date,
                home_score,
                away_score
            )
        )

        self.connection.commit()
        return self.cursor.lastrowid

    def update_match(
        self,
        *,
        match_id,
        home_team_id,
        away_team_id,
        match_date=None,
        home_score=None,
        away_score=None
    ):
        """
            Uppdaterar en befintlig match.
        """
        try:
            self.cursor.execute(
                """
                    UPDATE matches
                    SET
                        home_team_id = ?,
                        away_team_id = ?,
                        match_date = ?,
                        home_score = ?,
                        away_score = ?
                    WHERE id = ?
            """,
                (
                    home_team_id,
                    away_team_id,
                    match_date,
                    home_score,
                    away_score,
                    match_id
                )
            )
            self.connection.commit()
            return self.cursor.rowcount > 0

        except sqlite3.IntegrityError:
            raise ValueError("Matchen finns redan.")

    def match_exists(self, season_id, home_team_id, away_team_id, exclude_match_id=None):
        """
            Kontrollerar om en match redan finns.
        """
        query = """
            SELECT 1
            FROM matches
            WHERE season_id = ?
            AND home_team_id = ?
            AND away_team_id = ?
        """

        params = [
            season_id,
            home_team_id,
            away_team_id
        ]

        if exclude_match_id is not None:
            query += " AND id != ?"
            params.append(exclude_match_id)

        self.cursor.execute(query, params)
        return self.cursor.fetchone() is not None

    def update_match_score(self, coupon_id, match_number, home_score, away_score):
        """
            Uppdaterar resultatet för en match.
        """
        self.cursor.execute(
            """
                UPDATE matches
                SET home_score = ?,
                away_score = ?
                WHERE id = (
                SELECT match_id
                FROM coupon_matches
                WHERE coupon_id = ?
                AND match_number = ?
        )
            """, (
                home_score,
                away_score,
                coupon_id,
                match_number
            )
        )
        self.connection.commit()

    def get_head_to_head_matches(
        self,
        home_team_id,
        away_team_id
    ):
        """
            Hämtar tidigare möten mellan två lag.
        """
        self.cursor.execute(
            """
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
                WHERE
                    (
                        (
                            m.home_team_id = ?
                            AND m.away_team_id = ?
                        )
                        OR
                        (
                            m.home_team_id = ?
                            AND m.away_team_id = ?
                        )
                    )
                    AND m.home_score IS NOT NULL
                    AND m.away_score IS NOT NULL

                ORDER BY
                    m.match_date DESC
            """,
            (
                home_team_id,
                away_team_id,
                away_team_id,
                home_team_id
            )
        )
        rows = self.cursor.fetchall()
        matches = []

        for row in rows:
            match = self.factory.create_soccer_match(row)
            matches.append(match)

        return matches
