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
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_id INTEGER NOT NULL,
            match_number INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            FOREIGN KEY (coupon_id)
                REFERENCES coupons(id)
                ON DELETE CASCADE
        )
        """,

            """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            result TEXT NOT NULL,
            FOREIGN KEY (match_id)
                REFERENCES matches(id)
                ON DELETE CASCADE
        )
        """]
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
    def add_match(self, coupon_id, match_number, home_team, away_team):
        self.cursor.execute("""
        INSERT INTO matches(
            coupon_id,
            match_number,
            home_team,
            away_team
        )
        VALUES (?, ?, ?, ?)
        """, (
            coupon_id,
            match_number,
            home_team,
            away_team
        ))
        self.conn.commit()

    # Funktion som returnerar alla matcher för en viss tipskupong.
    def get_matches(self, coupon_id):
        self.cursor.execute("""
            SELECT match_number, home_team, away_team
            FROM matches
            WHERE coupon_id = ?
            ORDER BY match_number
        """, (coupon_id,))
        return self.cursor.fetchall()

    # Funktion som lagrar ett matchresultat i databasen.
    def set_result(self, match_id, result):
        self.cursor.execute("""
            INSERT INTO results(match_id, result)
            VALUES (?, ?)
            ON CONFLICT(match_id) DO UPDATE SET result = excluded.result
        """, (match_id, result))
        self.conn.commit()

    # Funktion som stänger ner databasanslutningen.
    def close(self):
        self.conn.close()
