from database.repositories.repository import Repository


class CouponRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    # Funktion som lagrar en tipskupong för år 'year' och vecka 'week' i databasen.
    # Funktionen returnerar det rad-id som aktualiseras för kupongen.
    def create_coupon(self, year, week):
        self.cursor.execute("""
            INSERT INTO coupons(year, week)
            VALUES(?, ?)
        """, (year, week))

        self.connection.commit()

        return self.cursor.lastrowid

    # Funktion som returnerar alla tipskuponger, som lagts till i databasen.
    def get_all_coupons(self):
        self.cursor.execute("""
        SELECT id, year, week
        FROM coupons
        """)

        return self.cursor.fetchall()

    # Funktion som returnerar en kupong (som en 'tuple') med hjälp av en tipskupongs id.
    def get_coupon(self, coupon_id):
        self.cursor.execute("""
            SELECT id, year, week
            FROM coupons
            WHERE id= ?
            """, (coupon_id,))

        return self.cursor.fetchone()

    # Funktion som returnerar den tipskupong för år=year och månad=week.
    def get_coupon_by_year_week(self, year, week):
        self.cursor.execute("""
            SELECT id, coupon_year, coupon_week
            FROM coupons
            WHERE coupon_year= ?
            AND coupon_week= ?
            """, (year, week))

        return self.cursor.fetchone()

    # Funktion som lägger till en match på en kupong.
    def add_coupon_match(self, coupon_id, match_number, match_id):
        self.cursor.execute("""
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
        ))

        self.connection.commit()

    # Funktion som returnerar alla matcher för en viss tipskupong.

    def get_coupon_matches(self, coupon_id):
        self.cursor.execute("""
        SELECT
            cm.match_number,

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

        FROM coupon_matches cm

        JOIN matches m
            ON cm.match_id = m.id

        JOIN seasons s
            ON m.season_id = s.id

        JOIN competitions c
            ON s.competition_id = c.id

        JOIN teams ht
            ON m.home_team_id = ht.id

        JOIN teams at
            ON m.away_team_id = at.id

        WHERE cm.coupon_id = ?

        ORDER BY cm.match_number

        """, (coupon_id,))

        return self.cursor.fetchall()
