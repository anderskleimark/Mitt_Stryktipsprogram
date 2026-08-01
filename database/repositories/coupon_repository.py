from database.repositories.repository import Repository


class CouponRepository(Repository):
    """
        Klass som hanterar kuponger och deras matcher i databasen.
    """

    def __init__(self, database):
        super().__init__(database)

    def add_coupon(self, year, week):
        """
            Lägger till en ny kupong.
        """
        self.cursor.execute(
            """
                INSERT INTO coupons(year, week)
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
                    id              AS coupon_id, 
                    coupon_year, 
                    coupon_week
                FROM coupons
            """
        )
        rows = self.cursor.fetchall()
        coupons = []
        for row in rows:
            coupon = self.factory.create_coupon(row)
            coupons.append(coupon)

        return coupons

    def get_coupon(self, coupon_id):
        """
            Hämtar en kupong via id.
        """
        self.cursor.execute(
            """
                SELECT 
                    id              AS coupon_id, 
                    coupon_year, 
                    coupon_week
                FROM coupons
                WHERE id= ?
            """,
            (coupon_id,)
        )

        row = self.cursor.fetchone()
        coupon = None
        if row:
            coupon = self.factory.create_coupon(row)

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
        coupon = None
        if row:
            coupon = self.factory.create_coupon(row)

        return coupon

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
                    cm.match_number             AS coupon_match_number,
                    m.id                        AS match_id,
                    m.match_date                AS match_date,
                    m.home_score                AS home_score,
                    m.away_score                AS away_score,
                    s.id                        AS season_id,
                    s.start_year                AS start_year,
                    s.end_year                  AS end_year,
                    c.id                        AS coupon_id,
                    com.competition_name        AS competition_name,
                    home_country.id             AS home_country_id,
                    home_country.country_name   AS home_country_name,
                    home_country.iso_code       AS home_country_code,
                    away_country.id             AS away_country_id,
                    away_country.country_name   AS away_country_name,
                    away_country.iso_code       AS away_country_code,
                    ht.id                       AS home_team_id,
                    ht.team_name                AS home_team_name,
                    ht.display_name             AS home_team_name,
                    at.id                       AS away_team_id,
                    at.team_name                AS away_team_name,
                    at.display_name             AS away_team_name
                FROM coupon_matches cm
                JOIN matches m
                    ON cm.match_id=m.id
                JOIN coupons c
                    ON c.id=cm.coupon_id
                JOIN seasons s
                    ON s.id=m.season_id
                JOIN competitions com
                    ON com.id=s.competition_id
                JOIN countries home_country
                    ON home_country.id=ht.country_id
                JOIN countries away_country
                    ON away_country.id=at.country_id                
                JOIN teams ht
                    ON ht.id=m.home_team_id
                JOIN teams at
                    ON at.id=m.away_team_id
                WHERE cm.coupon_id = ?
                ORDER BY cm.match_number
            """,
            (coupon_id,)
        )
        rows = self.cursor.fetchall()
        coupon_matches = []
        for row in rows:
            coupon_match = self.factory.create_coupon_match(row)
            coupon_matches.append(coupon_match)
        return coupon_matches
