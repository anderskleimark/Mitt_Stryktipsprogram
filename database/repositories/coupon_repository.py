from database.repositories.repository import Repository


class CouponRepository(Repository):
    """
        Klass som hanterar kuponger och deras matcher i databasen.
    """

    def add_coupon(self, year, week):
        """
            Lägger till en ny kupong.
        """
        self.cursor.execute(
            """
                INSERT INTO coupons(coupon_year, coupon_week)
                VALUES(?, ?)
            """,
            (year, week)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_coupons(self):
        """
            Hämtar alla kuponger.
        """

        self.cursor.execute(
            """
                SELECT
                    id AS coupon_id,
                    coupon_year,
                    coupon_week
                FROM coupons
                ORDER by coupon_year DESC, coupon_week DESC
            """
        )

        rows = self.cursor.fetchall()
        coupons = []

        for row in rows:
            coupon = self.factory.create_coupon(row)
            coupon.soccer_matches = self.get_coupon_matches(
                coupon.id
            )
            coupons.append(coupon)

        return coupons

    def get_coupon(self, coupon_id):
        """
            Hämtar en kupong via id inklusive matcher.
        """
        self.cursor.execute(
            """
                SELECT
                    id AS coupon_id,
                    coupon_year,
                    coupon_week
                FROM coupons
                WHERE id = ?
            """,
            (coupon_id,)
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        coupon = self.factory.create_coupon(row)

        coupon.soccer_matches = self.get_coupon_matches(
            coupon.id
        )

        return coupon

    def get_coupon_by_year_week(self, year, week):
        """
            Hämtar en kupong via år och vecka.
        """
        self.cursor.execute(
            """
                SELECT 
                    id              AS coupon_id, 
                    coupon_year, 
                    coupon_week
                FROM coupons
                WHERE coupon_year= ?
                AND coupon_week= ?
            """,
            (year, week)
        )
        row = self.cursor.fetchone()

        if row is None:
            return None

        coupon = self.factory.create_coupon(row)

        coupon.soccer_matches = self.get_coupon_matches(
            coupon.id
        )

        return coupon

    def delete_coupon(self, coupon_id):
        """
            Raderar en kupong.
        """

    def add_coupon_match(self, coupon_id, match_number, match_id):
        """
            Lägger till en match på en kupong.
        """
        self.cursor.execute(
            """
                INSERT INTO coupon_matches(
                    coupon_id,
                    match_number,
                    match_id
                )
                VALUES(?, ?, ?)
            """, (
                coupon_id,
                match_number,
                match_id
            )
        )
        self.connection.commit()

    def get_coupon_matches(self, coupon_id):
        """
        Hämtar alla matcher för en kupong.
        """
        self.cursor.execute(
            """
            SELECT
                cm.match_number                     AS coupon_match_number,
                m.id                                AS soccer_match_id,
                m.match_date                        AS soccer_match_date,
                m.home_score                        AS soccer_match_home_score,
                m.away_score                        AS soccer_match_away_score,
                s.id                                AS soccer_match_season_id,
                s.start_year                        AS soccer_match_season_start_year,
                s.end_year                          AS soccer_match_season_end_year,
                com.id                              AS soccer_match_competition_id,
                com.competition_name                AS soccer_match_competition_name,
                competition_country.id              AS soccer_match_competition_country_id,
                competition_country.country_name    AS soccer_match_competition_country_name,
                competition_country.iso_code        AS soccer_match_competition_country_code,
                ht.id                               AS soccer_match_home_team_id,
                ht.team_name                        AS soccer_match_home_team_name,
                ht.display_name                     AS soccer_match_home_team_display_name,
                home_country.id                     AS soccer_match_home_team_country_id,
                home_country.country_name           AS soccer_match_home_team_country_name,
                home_country.iso_code               AS soccer_match_home_team_country_code,
                at.id                               AS soccer_match_away_team_id,
                at.team_name                        AS soccer_match_away_team_name,
                at.display_name                     AS soccer_match_away_team_display_name,
                away_country.id                     AS soccer_match_away_team_country_id,
                away_country.country_name           AS soccer_match_away_team_country_name,
                away_country.iso_code               AS soccer_match_away_team_country_code
            FROM coupon_matches cm
            JOIN matches m
                ON m.id = cm.match_id
            JOIN seasons s
                ON s.id = m.season_id
            JOIN competitions com
                ON com.id = s.competition_id
            JOIN countries competition_country
                ON competition_country.id = com.country_id
            JOIN teams ht
                ON ht.id = m.home_team_id
            JOIN countries home_country
                ON home_country.id = ht.country_id
            JOIN teams at
                ON at.id = m.away_team_id
            JOIN countries away_country
                ON away_country.id = at.country_id
            WHERE cm.coupon_id = ?
            ORDER BY cm.match_number
            """,
            (coupon_id,)
        )

        rows = self.cursor.fetchall()
        coupon_matches = []

        for row in rows:
            coupon_matches.append(
                self.factory.create_coupon_match(row)
            )

        return coupon_matches
