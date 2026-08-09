import sqlite3
from pathlib import Path

from .repositories.bet_repository import BetRepository
from .repositories.competition_repository import CompetitionRepository
from .repositories.country_repository import CountryRepository
from .repositories.coupon_repository import CouponRepository
from .repositories.season_repository import SeasonRepository
from .repositories.setting_repository import SettingRepository
from .repositories.soccer_match_repository import SoccerMatchRepository
from .repositories.system_repository import SystemRepository
from .repositories.team_repository import TeamRepository


class Database:
    DATABASE_PATH = Path(__file__).parent / "stryktips.db"
    SCHEMA_DIR = "schema"
    DATA_DIR = "data"
    FILE_PATTERN = "*.sql"
    ENCODING = "utf-8"

    def __init__(self):
        self.connection = sqlite3.connect(self.DATABASE_PATH)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.create_database_tables()
        self.load_initial_data()

        # Repositories.
        self.team_repository = TeamRepository(self)
        self.competition_repository = CompetitionRepository(self)
        self.season_repository = SeasonRepository(self)
        self.soccer_match_repository = SoccerMatchRepository(self)
        self.system_repository = SystemRepository(self)
        self.bet_repository = BetRepository(self)
        self.coupon_repository = CouponRepository(self)
        self.country_repository = CountryRepository(self)
        self.setting_repository = SettingRepository(self)

    def create_database_tables(self):
        schema_path = (
            Path(__file__).parent /
            self.SCHEMA_DIR
        )

        for file in sorted(schema_path.glob(self.FILE_PATTERN)):
            with open(file, encoding=self.ENCODING) as f:
                sql = f.read()

            self.cursor.executescript(sql)

        self.connection.commit()

    def load_initial_data(self):
        data_path = Path(__file__).parent / self.DATA_DIR

        for file in sorted(data_path.glob(self.FILE_PATTERN)):
            with open(file, encoding=self.ENCODING) as f:
                sql = f.read()

            self.cursor.executescript(sql)

        self.connection.commit()

    def close(self):
        self.connection.close()
