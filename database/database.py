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
        CREATE TABLE IF NOT EXISTS leagues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        country TEXT NOT NULL)
        """,

            """
        CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        league_id INTEGER NOT NULL,
        start_year INTEGER NOT NULL,
        end_year INTEGER NOT NULL,
        FOREIGN KEY(league_id)
        REFERENCES leagues(id)
        ON DELETE CASCADE,
        UNIQUE(league_id, start_year, end_year)
        )

        """,

            """
        CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_id INTEGER NOT NULL,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        match_date TEXT,
        home_score INTEGER,
        away_score INTEGER,
        FOREIGN KEY(season_id)
        REFERENCES seasons(id),
        FOREIGN KEY(home_team_id)
        REFERENCES teams(id),
        FOREIGN KEY(away_team_id)
        REFERENCES teams(id),
        UNIQUE(season_id, home_team_id, away_team_id)
        )
        """,

            """
        CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        week INTEGER NOT NULL,
        UNIQUE(year, week)
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS coupon_matches (
        coupon_id INTEGER NOT NULL,
        match_number INTEGER NOT NULL,
        match_id INTEGER NOT NULL,
        PRIMARY KEY(coupon_id, match_number),
        FOREIGN KEY(coupon_id)
        REFERENCES coupons(id)
        ON DELETE CASCADE,
        FOREIGN KEY(match_id)
        REFERENCES matches(id),
        UNIQUE(coupon_id, match_id)
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
        correct_count INTEGER,
        prize INTEGER,
        FOREIGN KEY(coupon_id)
        REFERENCES coupons(id),
        FOREIGN KEY(system_id)
        REFERENCES systems(id)
        )
        """,
            """
        CREATE TABLE IF NOT EXISTS bet_details (
        bet_id INTEGER NOT NULL,
        match_number INTEGER NOT NULL,
        frame_value TEXT NOT NULL,
        key_value TEXT,
        PRIMARY KEY(bet_id, match_number),
        FOREIGN KEY(bet_id)
        REFERENCES bets(id)
        ON DELETE CASCADE
        )
        """
        ]

        for query in queries:
            self.cursor.execute(query)

        self.conn.commit()

    def get_all_seasons(self):

        self.cursor.execute("""
            SELECT
                seasons.id,
                leagues.name,
                seasons.start_year,
                seasons.end_year

            FROM seasons

            JOIN leagues
                ON seasons.league_id = leagues.id

            ORDER BY leagues.name, seasons.start_year
        """)

        return self.cursor.fetchall()

    def get_team_id(self, team_name):

        self.cursor.execute("""
        SELECT id
        FROM teams
        WHERE name = ?
        """, (team_name,))

        row = self.cursor.fetchone()

        if row:
            return row[0]

        self.cursor.execute("""
            INSERT INTO teams(name)
            VALUES(?)
        """, (team_name,))

        self.conn.commit()

        return self.cursor.lastrowid

    # Funktion som lagrar en tipskupong för år 'year' och vecka 'week' i databasen.
    # Funktionen returnerar det rad-id som aktualiseras för kupongen.

    def create_coupon(self, year, week):
        self.cursor.execute("""
            INSERT INTO coupons(year, week)
            VALUES(?, ?)
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
            SELECT id, year, week
            FROM coupons
            WHERE year= ?
            AND week= ?
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

        self.conn.commit()

    # Funktion som lägger till en match i databasen.
    def add_match(self, season_id, home_team_id, away_team_id):

        self.cursor.execute("""
        INSERT INTO matches(
        season_id,
        home_team_id,
        away_team_id
        )
        VALUES(?, ?, ?)
        """, (
            season_id,
            home_team_id,
            away_team_id
        ))

        self.conn.commit()
        return self.cursor.lastrowid

    # Funktion som returnerar alla matcher för en viss tipskupong.
    def get_coupon_matches(self, coupon_id):
        self.cursor.execute("""
        SELECT
            cm.match_number,
            m.id,
            m.season_id,
            ht.name,
            at.name,
            m.home_score,
            m.away_score

        FROM coupon_matches cm

        JOIN matches m
            ON cm.match_id = m.id

        JOIN teams ht
            ON m.home_team_id = ht.id

        JOIN teams at
            ON m.away_team_id = at.id

        WHERE cm.coupon_id = ?

        ORDER BY cm.match_number

        """, (coupon_id,))

        return self.cursor.fetchall()

    # Funktion som sparar ett matchresultat i databasen.

    def update_match_score(self, coupon_id, match_number, home_score, away_score):

        self.cursor.execute("""
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
                VALUES(?, ?, ?, ?)
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

    # Funktion som hämtar information om ett tipssystem.
    def get_system_row(self, system_id):
        self.cursor.execute("""
            SELECT
                id,
                system_type,
                full_covers,
                half_covers,
                rows
            FROM systems
            WHERE id= ?
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
            WHERE id= ?
            """, (system_id,))

        self.conn.commit()

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

        self.conn.commit()

        return self.cursor.lastrowid

    # Funktion som hämtar alla vad ur databasen.
    def get_all_bets(self):

        self.cursor.execute("""
            SELECT
                id,
                coupon_id,
                system_id,
                date,
                correct_count,
                prize

            FROM bets

            ORDER BY date DESC
        """)

        return self.cursor.fetchall()

    # Funtkion som hämtar detaljer om ett angivet vad.
    def get_bet_details(self, bet_id):

        self.cursor.execute("""
        SELECT
            bet_id,
            match_number,
            frame_value,
            key_value

        FROM bet_details
        WHERE bet_id = ?
        ORDER BY match_number
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

        self.conn.commit()

    # Funktion som stänger ner databasanslutningen.
    def close(self):
        self.conn.close()
