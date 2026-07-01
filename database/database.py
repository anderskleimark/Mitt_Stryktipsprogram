import sqlite3
import os

# Klass för att hantera databasen (sqlite).


class Database:

    DATABASE_NAME = "stryktips.db"

    def __init__(self):
        database_exists = os.path.exists(self.DATABASE_NAME)

        self.conn = sqlite3.connect(self.DATABASE_NAME)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.create_database_tables()

    # Funktion som skapar databastabellerna.

    def create_database_tables(self):
        print("create_database_tables")

        queries = [

            """
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            UNIQUE(year, week)
        )
        """,

            """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_id INTEGER NOT NULL,
            game_number INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            FOREIGN KEY (coupon_id)
                REFERENCES coupons(id)
                ON DELETE CASCADE
        )
        """,

            """
        CREATE TABLE IF NOT EXISTS systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_type TEXT NOT NULL,
            full_covers INTEGER NOT NULL,
            half_covers INTEGER NOT NULL,
            rows INTEGER NOT NULL,
            UNIQUE(system_type, full_covers, half_covers, rows)
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_id INTEGER NOT NULL,
            system_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            correct INTEGER,
            prize INTEGER,
            FOREIGN KEY (coupon_id) REFERENCES coupons(id),
            FOREIGN KEY (system_id) REFERENCES systems(id)
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS bet_details (
            bet_id INTEGER PRIMARY KEY,
            system_frame TEXT NOT NULL,
            key_row TEXT,
            FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE CASCADE
        )
        """
        ]

        for query in queries:
            self.cursor.execute(query)

        self.conn.commit()

    # Funktion som lagrar en tipskupong för år 'year' och vecka 'week' i databasen.
    # Funktionen returnerar det rad-id som aktualiseras för kupongen.
    def create_coupon(self, year, week):
        self.cursor.execute("""
            INSERT INTO coupons(year, week)
            VALUES (?, ?)
        """, (year, week))

        self.conn.commit()

        return self.cursor.lastrowid

    # Funktion som returnerar alla tipskuponger, som lagts till i databasen.
    def get_all_coupons(self):
        self.cursor.execute("""
        SELECT id, year, week
        FROM coupons
        ORDER BY year DESC, week DESC
        """)

        return self.cursor.fetchall()

    def get_coupon(self, coupon_id):

        self.cursor.execute("""
            SELECT id, year, week
            FROM coupons
            WHERE id = ?
        """, (coupon_id,))

        return self.cursor.fetchone()

    # Funktion som returnerar den tipskupong för år=year och månad=week.

    def get_coupon_by_year_week(self, year, week):

        self.cursor.execute("""
            SELECT id, year, week
            FROM coupons
            WHERE year = ?
            AND week = ?
        """, (year, week))

        return self.cursor.fetchone()

    # Funktion som lägger till en tipsmatch i databasen.
    def add_game(self, coupon_id, game_number, home_team, away_team):

        self.cursor.execute("""
            INSERT INTO games(
                coupon_id,
                game_number,
                home_team,
                away_team
            )
            VALUES (?, ?, ?, ?)
        """, (
            coupon_id,
            game_number,
            home_team,
            away_team
        ))

        self.conn.commit()

    # Funktion som returnerar alla matcher för en viss tipskupong.
    def get_games(self, coupon_id):

        self.cursor.execute("""
            SELECT game_number,
                   home_team,
                   away_team,
                   home_score,
                   away_score
            FROM games
            WHERE coupon_id = ?
            ORDER BY game_number
        """, (coupon_id,))

        return self.cursor.fetchall()

    # Funktion som lagrar ett matchresultat i databasen.
    def update_game_score(self, coupon_id, game_number, home_score, away_score):

        self.cursor.execute("""
            UPDATE games
            SET home_score = ?,
                away_score = ?
            WHERE coupon_id = ?
              AND game_number = ?
        """, (
            home_score,
            away_score,
            coupon_id,
            game_number
        ))

        self.conn.commit()

    # Funktion som skapar ett nytt tipssystem i databasen med hjälp
    # av typ av system, antalet helgarderingar, antalet halvgarderingar och antalet rader.
    # Funktionen returnerar det id som tipssystemet får.
    def create_system(
        self,
        system_type,
        full_covers,
        half_covers,
        rows
    ):

        try:
            self.cursor.execute("""
                INSERT INTO systems(
                    system_type,
                    full_covers,
                    half_covers,
                    rows
                )
                VALUES (?, ?, ?, ?)
            """, (
                system_type,
                full_covers,
                half_covers,
                rows
            ))

            self.conn.commit()
            return self.cursor.lastrowid

        except sqlite3.IntegrityError:
            raise ValueError(
                f"Tipssystemet finns redan."
            )

    def get_system_row(self, system_id):
        self.cursor.execute("""
            SELECT
                id,
                system_type,
                full_covers,
                half_covers,
                rows
            FROM systems
            WHERE id = ?
        """, (system_id,))

        return self.cursor.fetchone()

    # Funktion som returnerar alla tipssystem som finns tillagda i databasen.
    def get_all_systems(self):

        self.cursor.execute("""
            SELECT id, system_type, full_covers, half_covers, rows
            FROM systems
            ORDER BY id
        """)

        return self.cursor.fetchall()

    # Funktion som raderar ett tipssystem.
    def delete_system(self, system_id):

        self.cursor.execute("""
            DELETE FROM systems
            WHERE id = ?
            """, (system_id,))

        self.conn.commit()

    def create_bet(self, coupon_id, system_id, date):

        self.cursor.execute("""
            INSERT INTO bets(
                coupon_id,
                system_id,
                date
            )
            VALUES (?, ?, ?)
        """, (
            coupon_id,
            system_id,
            date
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def get_all_bets(self):

        self.cursor.execute("""
            SELECT
                id,
                coupon_id,
                system_id,
                date,
                correct,
                prize

            FROM bets

            ORDER BY date DESC
        """)

        return self.cursor.fetchall()

    def get_bet_details(self, bet_id):

        self.cursor.execute("""
            SELECT
                bet_id,
                system_frame,
                key_row
            FROM bet_details
            WHERE bet_id = ?
        """, (bet_id,))

        return self.cursor.fetchone()

    # Funktion som stänger ner databasanslutningen.
    def close(self):
        self.conn.close()
