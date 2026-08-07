from database.repositories.repository import Repository


class BetRepository(Repository):
    """
        Klass som hanterar vad och vadets detaljer i databasen.
    """

    def add_bet(self, coupon_id, system_id, bet_date):
        """
            Lägger till ett nytt vad.
        """
        self.cursor.execute(
            """
                INSERT INTO bets(
                    coupon_id,
                    system_id,
                    bet_date
                )
                VALUES(?, ?, ?)
            """, (
                coupon_id,
                system_id,
                bet_date
            )
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_bets(self):
        """
            Hämtar alla vad.
        """
        self.cursor.execute(
            """
                SELECT
                    b.id                    AS bet_id,
                    b.bet_date              AS bet_date,
                    b.correct_count         AS correct_count,
                    b.prize                 AS prize,
                    c.id                    AS coupon_id,
                    c.coupon_year           AS coupon_year,
                    c.coupon_week           AS coupon_week,
                    s.id                    AS system_id,
                    s.system_type           AS system_type,
                    s.full_covers           AS full_covers,
                    s.half_covers           AS half_covers,
                    s.row_count             AS row_count
                FROM bets b
                JOIN coupons c
                    ON b.coupon_id=c.id
                JOIN systems s
                    ON b.system_id=s.id
                ORDER BY c.coupon_year DESC, c.coupon_week DESC
                   
            """
        )
        rows = self.cursor.fetchall()
        bets = []
        for row in rows:
            bet = self.factory.create_bet(row)
            bets.append(bet)
        return bets

    def get_bet(self, bet_id):
        """
            Hämtar ett vad via id.
        """

        self.cursor.execute(
            """
                SELECT                    
                    b.id                    AS bet_id,
                    b.bet_date              AS bet_date,     
                    b.correct_count         AS correct_count,
                    b.prize                 AS prize,
                    c.id                    AS coupon_id,
                    c.coupon_year           AS coupon_year,
                    c.coupon_week           AS coupon_week,
                    s.id                    AS system_id,
                    s.system_type           AS system_type,
                    s.full_covers           AS full_covers,
                    s.half_covers           AS half_covers,
                    s.row_count             AS row_count
                FROM bets b
                JOIN coupons c
                    ON b.coupon_id=c.id
                JOIN systems s
                    ON b.system_id=s.id
                WHERE b.id = ?
            """, (bet_id,)
        )
        row = self.cursor.fetchone()
        bet = None
        if row:
            bet = self.factory.create_bet(row)
        return bet

    def get_bet_details(self, bet_id):
        """
            Hämtar detaljer för ett vad.
        """
        self.cursor.execute(
            """
                SELECT
                    b.id                        AS bet_id,
                    b.bet_date,
                    b.correct_count,
                    b.prize,                    
                    bd.match_number             AS bet_details_match_number,
                    bd.frame_value              AS bet_details_frame_value,
                    bd.key_value                AS bet_details_key_value,
                    bd.mathematical_value       AS bet_details_mathematical_value
                FROM bets b
                JOIN bet_details bd
                    ON b.id=bd.bet_id
                WHERE bd.bet_id = ?
                ORDER BY bd.match_number
            """,
            (bet_id,)
        )
        rows = self.cursor.fetchall()
        bet_details = []
        for row in rows:
            bet_detail = self.factory.create_bet_details(row)
            bet_details.append(bet_detail)
        return bet_details

    def update_bet_result(
        self,
        bet_id,
        correct_count,
        prize
    ):
        """
            Uppdaterar resultat och vinst för ett vad.
        """
        self.cursor.execute(
            """
                UPDATE bets
                SET correct_count= ?,
                prize= ?
                WHERE id= ?
            """, (
                correct_count,
                prize,
                bet_id
            )
        )
        self.connection.commit()

    def save_detail(self, bet_id, match_number, frame=None, key=None):
        """
            Sparar eller uppdaterar ram och U-tecken för en match.
        """
        self.cursor.execute(
            """
                INSERT INTO bet_details(
                    bet_id,
                    match_number,
                    frame_value,
                    key_value
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(
                    bet_id,
                    match_number
                )
                DO UPDATE SET
                    frame_value = COALESCE(excluded.frame_value, frame_value),
                    key_value = COALESCE(excluded.key_value, key_value)
            """, (
                bet_id,
                match_number,
                frame,
                key
            )
        )
        self.connection.commit()

    def delete_bet(self, bet_id):
        """
            Raderar ett vad.
        """
        self.cursor.execute(
            """
                DELETE FROM bets
                WHERE id = ?
            """,
            (bet_id,)
        )
        self.connection.commit()
        return self.cursor.rowcount > 0

    def save_mathematical_value(self, bet_id, match_number, checked):
        """
            Sparar värdet för matematisk gardering för en match.
        """
        self.cursor.execute(
            """
                UPDATE bet_details
                SET mathematical_value = ?
                WHERE bet_id = ?
                AND match_number = ?
            """,
            (
                checked,
                bet_id,
                match_number
            )
        )
        self.connection.commit()

    def save_key(self, bet_id, match_number, key):
        """
            Sparar U-tecken för en match.
        """
        self.cursor.execute(
            """
                UPDATE bet_details
                SET key_value = ?
                WHERE bet_id = ?
                AND match_number = ?
            """, (
                key,
                bet_id,
                match_number
            )
        )
        self.connection.commit()
