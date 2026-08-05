from database.repositories.repository import Repository


class SoccerMatchRepository(Repository):
    """
        Klass som hanterar matcher i databasen.
    """

    def __init__(self, database):
        super().__init__(database)

    def get_matches(self, season_id, team_id=None, venue="all"):
        """
            Hämtar alla matcher för en säsong. Om team_id anges, 
            så hämtas alla matcher för det laget (hemma och borta).
            Med hjälp av venue kan man filtrera på hemma- och bortamatcher.
        """
        query = """
            SELECT
                matches.id                      AS soccer_match_id,
                seasons.id                      AS soccer_match_season_id,
                seasons.start_year              AS soccer_match_season_start_year,
                seasons.end_year                AS soccer_match_season_end_year,
                competitions.id                 AS soccer_match_competition_id,
                countries.id                    AS soccer_match_competition_country_id,
                countries.country_name          AS soccer_match_competition_country_name,
                countries.iso_code              AS soccer_match_competition_country_code,
                competitions.competition_name   AS soccer_match_competition_name,
                ht.id                           AS soccer_match_home_team_id,
                ht.country_id                   AS soccer_match_home_team_country_id,
                ht.team_name                    AS soccer_match_home_team_name,
                ht.display_name                 AS soccer_match_home_team_display_name,
                home_country.id                 AS soccer_match_home_team_country_id,
                home_country.country_name       AS soccer_match_home_team_country_name,
                home_country.iso_code           AS soccer_match_home_team_country_code,
                at.id                           AS soccer_match_away_team_id,
                at.country_id                   AS soccer_match_away_team_country_id,
                at.team_name                    AS soccer_match_away_team_name,
                at.display_name                 AS soccer_match_away_team_display_name,
                away_country.id                 AS soccer_match_away_team_country_id,
                away_country.country_name       AS soccer_match_away_team_country_name,
                away_country.iso_code           AS soccer_match_away_team_country_code,
                match_date                      AS soccer_match_date,
                home_score                      AS soccer_match_home_score,      
                away_score                      AS soccer_match_away_score                    
            FROM matches
            JOIN seasons
                ON seasons.id=matches.season_id
            JOIN competitions
                ON competitions.id=seasons.competition_id
            JOIN countries
                ON countries.id = competitions.country_id
            JOIN teams ht
                ON ht.id = matches.home_team_id
            JOIN teams at
                ON at.id = matches.away_team_id
            JOIN countries home_country
                ON home_country.id = ht.country_id
            JOIN countries away_country
                ON away_country.id = at.country_id
            WHERE matches.season_id = ?
        """
        parameters = [season_id]
        if team_id is not None:
            if venue == "home":
                query += """
                AND matches.home_team_id = ?
                """
                parameters.append(team_id)

            elif venue == "away":
                query += """
                AND matches.away_team_id = ?
                """
                parameters.append(team_id)

            else:
                query += """
                AND (
                    matches.home_team_id = ?
                    OR matches.away_team_id = ?
                )
                """
                parameters.extend([team_id, team_id])

        query += """
            ORDER BY matches.match_date DESC
        """

        self.cursor.execute(query, parameters)
        rows = self.cursor.fetchall()

        soccer_matches = []

        for row in rows:
            soccer_match = self.factory.create_soccer_match(row)
            soccer_matches.append(soccer_match)

        return soccer_matches

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

        query = """
            SELECT
                m.id AS soccer_match_id,
                m.match_date AS soccer_match_date,
                m.home_score AS soccer_match_home_score,
                m.away_score AS soccer_match_away_score,

                s.id AS soccer_match_season_id,
                s.start_year AS soccer_match_season_start_year,
                s.end_year AS soccer_match_season_end_year,

                c.id AS soccer_match_competition_id,
                c.competition_name AS soccer_match_competition_name,

                country.id AS soccer_match_competition_country_id,
                country.country_name AS soccer_match_competition_country_name,
                country.iso_code AS soccer_match_competition_country_code,

                ht.id AS soccer_match_home_team_id,
                ht.team_name AS soccer_match_home_team_name,
                ht.display_name AS soccer_match_home_team_display_name,

                at.id AS soccer_match_away_team_id,
                at.team_name AS soccer_match_away_team_name,
                at.display_name AS soccer_match_away_team_display_name

            FROM matches m

            JOIN seasons s
                ON m.season_id = s.id

            JOIN competitions c
                ON s.competition_id = c.id

            JOIN countries country
                ON c.country_id = country.id

            JOIN teams ht
                ON m.home_team_id = ht.id

            JOIN teams at
                ON m.away_team_id = at.id

            WHERE
                (
                    (
                        m.home_team_id = ?
                        AND
                        m.away_team_id = ?
                    )
                    OR
                    (
                        m.home_team_id = ?
                        AND
                        m.away_team_id = ?
                    )
                )

                AND m.home_score IS NOT NULL
                AND m.away_score IS NOT NULL

            ORDER BY
                m.match_date DESC
        """

        parameters = (
            home_team_id,
            away_team_id,
            away_team_id,
            home_team_id
        )

        self.cursor.execute(query, parameters)

        rows = self.cursor.fetchall()

        matches = []

        for row in rows:
            match = self.factory.create_soccer_match(row)
            matches.append(match)

        return matches
