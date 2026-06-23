import sqlite3
import os


class Database:

    def __init__(self):
        database_exists = os.path.exists("stryktips.db")
        self.conn = sqlite3.connect("stryktips.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        if not database_exists:
            self.create_database_tables()

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

    def close(self):
        self.conn.close()
