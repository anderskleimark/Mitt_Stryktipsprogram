from database.repositories.repository import Repository


class BetRepository(Repository):
    def __init__(self, database):
        super().__init__(database)

    # Funktion som returnerar hur många vad som använder ett system.
    def get_bet_count_for_system(self, system_id):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM bets
            WHERE system_id = ?
        """, (system_id,))

        return self.cursor.fetchone()[0]

    # Funktion som lägger till ett vad i databasen.
    def create_bet(self, coupon_id, system_id, date):
        self.cursor.execute("""
            INSERT INTO bets(
                coupon_id,
                system_id,
                date
            )
            VALUES(?, ?, ?)
        """, (
            coupon_id,
            system_id,
            date
        ))

        self.connection.commit()

        return self.cursor.lastrowid

    # Funktion som hämtar alla vad ur databasen.
    def get_all_bets(self):
        self.cursor.execute("""
            SELECT
                b.id,
                b.bet_date,
                b.correct_count,
                b.prize,
                s.id AS system_id,
                s.system_type,
                s.full_covers,
                s.half_covers,
                s.row_count,
                c.id AS coupon_id,
                c.coupon_year,
                c.coupon_week
            FROM bets b
            JOIN systems s
                ON b.system_id = s.id
            JOIN coupons c
                ON b.coupon_id = c.id
            ORDER BY c.coupon_year DESC, c.coupon_week DESC
        """)

        return self.cursor.fetchall()

    # Funtkion som hämtar detaljer om ett angivet vad.
    def get_bet_details(self, bet_id):
        self.cursor.execute("""
        SELECT
            bd.match_number,
            bd.frame_value,
            bd.key_value,
            bd.mathematical,

            b.id,
            b.date,
            b.correct_count,
            b.prize

        FROM bet_details bd

        JOIN bets b
            ON bd.bet_id = b.id

        WHERE bd.bet_id = ?

        ORDER BY bd.match_number
        """, (bet_id,))

        return self.cursor.fetchall()

    # Funtkion som sparar ett vad.
    def update_bet_result(
        self,
        bet_id,
        correct_count,
        prize
    ):
        self.cursor.execute("""
            UPDATE bets
            SET correct_count= ?,
                prize= ?
            WHERE id= ?
        """, (
            correct_count,
            prize,
            bet_id
        ))

        self.connection.commit()

    # Funktion som sparar data om ett vad.
    def save_detail(self, bet_id, match_number, frame=None, key=None):
        self.cursor.execute("""
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
        ))

        self.connection.commit()

    # Funktion som raderar ett vad med hjälp av dess id.
    def delete_bet(self, bet_id):
        self.cursor.execute("""
            DELETE FROM bets
            WHERE id = ?
        """, (bet_id,))

        self.connection.commit()

    def save_mathematical_value(self, bet_id, match_number, checked):
        self.cursor.execute(
            """
            UPDATE bet_details
            SET mathematical = ?
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

     # Funktion som sparar ett U-tecken för ett vad med ett angivet match-nummer.
    def save_key(self, bet_id, match_number, key):
        self.cursor.execute("""
            UPDATE bet_details
            SET key_value = ?
            WHERE bet_id = ?
            AND match_number = ?
        """, (
            key,
            bet_id,
            match_number
        ))

        self.connection.commit()
