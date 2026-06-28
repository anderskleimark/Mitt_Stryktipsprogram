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

        if not database_exists:
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

    # Funktion som returnerar den tipskupong för år=year och månad=week.
    def get_coupon(self, year, week):
        self.cursor.execute("""
            SELECT id, year, week
            FROM coupons
            WHERE year = ? AND week = ?
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

    # Funktion som stänger ner databasanslutningen.
    def close(self):
        self.conn.close()
