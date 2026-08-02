from __future__ import annotations

from dataclasses import dataclass, field
from PySide6.QtGui import QIcon
from pathlib import Path


@dataclass
class AnalysisData:
    """
        Innehåller all information som behövs för att analysera en fotbollsmatch.
    """

    # Vald säsong.
    season: Season

    # Hemmalag.
    home_team: Team

    # Bortalag.
    away_team: Team

    # Hemmalagets tidigare matcher.
    home_matches: list

    # Bortalagets tidigare matcher.
    away_matches: list

    # Statistik för hela säsongen.
    season_statistics: SeasonStatistics

    # Beräknad statistik för hemmalaget.
    home_statistics: TeamStatistics | None

    # Beräknad statistik för bortalaget.
    away_statistics: TeamStatistics | None

    # Inbördes möten.
    h2h_statistics: HeadToHeadStatistics


@dataclass
class Bet:
    """
        Representerar ett spelat stryktips- eller oddsspel.
    """
    id: int
    bet_date: str
    correct_count: int | None = None
    prize: int | None = None
    total_cost: int | None = None
    system: System = None
    coupon: Coupon = None


@dataclass
class BetDetails:
    """
        Innehåller detaljer om ett vad.
    """
    bet: Bet
    match_number: int
    frame_value: str
    key_value: str | None = None
    mathematical_value: bool = False

# Representerar en fotbollstävling eller liga.


@dataclass
class Competition:
    """
        Representerar en fotbollstävling eller liga.
    """
    id: int
    competition_name: str
    country: Country

    @property
    def flag_path(self):
        return Country.get_flag_path(self.country.id)

    @property
    def display_name(self):
        return self.name


@dataclass
class Country:
    """
        Representerar ett land.
    """
    id: int
    country_name: str
    iso_code: str
    FLAG_CODES = {
        "Afghanistan": "af",
        "Albanien": "al",
        "Algeriet": "dz",
        "Andorra": "ad",
        "Angola": "ao",
        "Antigua och Barbuda": "ag",
        "Argentina": "ar",
        "Armenien": "am",
        "Australien": "au",
        "Azerbajdzjan": "az",

        "Belgien": "be",
        "Brasilien": "br",
        "Bulgarien": "bg",

        "Chile": "cl",
        "Colombia": "co",

        "Danmark": "dk",

        "England": "eng",

        "Finland": "fi",
        "Frankrike": "fr",

        "Ghana": "gh",
        "Grekland": "gr",

        "Indien": "in",
        "Irland": "ie",
        "Island": "is",
        "Italien": "it",

        "Japan": "jp",

        "Kanada": "ca",
        "Kina": "cn",
        "Kroatien": "hr",

        "Marocko": "ma",
        "Mexiko": "mx",

        "Nederländerna": "nl",
        "Norge": "no",
        "Nya Zeeland": "nz",

        "Polen": "pl",
        "Portugal": "pt",

        "Rumänien": "ro",
        "Ryssland": "ru",

        "Schweiz": "ch",
        "Serbien": "rs",
        "Skottland": "sct",
        "Spanien": "es",
        "Sverige": "se",
        "Sydafrika": "za",
        "Sydkorea": "kr",

        "Tjeckien": "cz",
        "Turkiet": "tr",
        "Tyskland": "de",

        "Ukraina": "ua",
        "Uruguay": "uy",
        "USA": "us",

        "Wales": "wls",

        "Österrike": "at",
    }

    @classmethod
    def get_flag_path(cls, country):
        """
        Returnerar sökvägen till landets flagga.
        Om landet saknas returneras unknown.png.
        """
        code = cls.FLAG_CODES.get(country)

        if code is None:
            return str(Path("resources") / "flags" / "unknown.png")

        return str(Path("resources") / "flags" / f"{code}.svg")

    @property
    def flag_path(self):
        return self.get_flag_path(self.country_name)

    @property
    def flag_icon(self):
        return QIcon(self.flag_path)

    @property
    def display_name(self):
        return self.country_name


@dataclass
class CouponMatch:
    """
        Kopplar ett matchnummer på kupongen till en fotbollsmatch.
    """
    match_number: int
    soccer_match: SoccerMatch
    coupon: Coupon


@dataclass
class Coupon:
    """
        Representerar en stryktipskupong.
    """
    id: int
    coupon_year: int
    coupon_week: int
    soccer_matches: list["CouponMatch"] = field(default_factory=list)


@dataclass
class HeadToHeadStatistics:
    """
        Innehåller statistik om inbördes möten.
    """
    matches: int
    home_wins: int
    home_draws: int
    home_losses: int
    home_score: str

    away_wins: int
    away_draws: int
    away_losses: int
    away_score: str


@dataclass
class MatchAnalysis:
    """
        Innehåller resultatet av en analys av en fotbollsmatch.
    """

    home_statistics: TeamStatistics
    away_statistics: TeamStatistics
    h2h_statistics: HeadToHeadStatistics

    lambda_home: float
    lambda_away: float

    # Sannolikhet för att respektive lag gör 0, 1, 2, ... mål.
    home_poisson: list[float]
    away_poisson: list[float]

    probability_1: float
    probability_x: float
    probability_2: float

    probability_over_25: float
    probability_under_25: float

    probability_btts: float

    score_matrix: list[list[float]]


@dataclass
class Season:
    """
        Representerar en säsong för en fotbollstävling.
    """
    id: int
    competition: Competition
    start_year: int
    end_year: int

    @property
    def name(self):
        if self.start_year == self.end_year:
            return str(self.start_year)
        return f"{self.start_year} / {self.end_year}"

    @property
    def display_name(self):
        return f"{self.competition.competition_name} {self.name}"


@dataclass
class SeasonStatistics:
    """
        Innehåller sammanfattande statistik för en hel säsong.
    """
    matches_played: int = 0
    total_home_goals: int = 0
    total_away_goals: int = 0

    @property
    def average_home_goals(self):
        if self.matches_played == 0:
            return 0.0
        return self.total_home_goals / self.matches_played

    @property
    def average_away_goals(self):
        if self.matches_played == 0:
            return 0.0
        return self.total_away_goals / self.matches_played

    @property
    def home_advantage(self):
        if self.average_away_goals == 0:
            return 1.0

        return (
            self.average_home_goals /
            self.average_away_goals
        )


@dataclass
class SoccerMatch:
    """
        Representerar en spelad eller kommande fotbollsmatch.
    """
    id: int
    season: Season
    home_team: Team
    away_team: Team
    match_date: str | None = None
    home_score: int | None = None
    away_score: int | None = None

    @property
    def result_1x2(self):
        if self.home_score is None or self.away_score is None:
            return ""

        if self.home_score > self.away_score:
            return "1"
        if self.home_score < self.away_score:
            return "2"

        return "X"


@dataclass
class Standing:
    """
        Representerar ett lags tabellplacering och statistik i en liga.
    """
    team: Team
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


@dataclass
class System:
    """
        Representerar ett matematiskt eller reducerat tipssystem.
    """
    id: int
    system_type: str
    full_covers: int
    half_covers: int
    row_count: int

    @property
    def type_name(self):
        return {
            "M": "M-system",
            "R": "R-system",
            "U": "U-system"
        }.get(self.system_type, self.system_type)

    @property
    def display_name(self):
        return (
            f"{self.system_type} "
            f"{self.full_covers}-"
            f"{self.half_covers}-"
            f"{self.row_count}"
        )


@dataclass
class Team:
    id: int
    country: Country
    team_name: str
    display_name: str


@dataclass
class TeamStatistics:
    """
        Innehåller statistik och modellparametrar för ett lag under en säsong.
    """

    team: Team
    season: Season
    matches_played: int = 0

    wins: int = 0
    draws: int = 0
    losses: int = 0
    home_wins: int = 0
    home_draws: int = 0
    home_losses: int = 0
    away_wins: int = 0
    away_draws: int = 0
    away_losses: int = 0

    goals_for: int = 0
    goals_against: int = 0

    home_matches_played: int = 0
    away_matches_played: int = 0

    home_goals_for: int = 0
    home_goals_against: int = 0

    away_goals_for: int = 0
    away_goals_against: int = 0

    home_attack_coefficient: float = 0.0
    home_defence_coefficient: float = 0.0
    away_attack_coefficient: float = 0.0
    away_defence_coefficient: float = 0.0

    recent_form: float = 1.0

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    @property
    def home_goal_difference(self):
        return self.home_goals_for - self.home_goals_against

    @property
    def away_goal_difference(self):
        return self.away_goals_for - self.away_goals_against

    @property
    def goals_for_against(self):
        return f"{self.goals_for} – {self.goals_against}"

    @property
    def home_goals_for_against(self):
        return f"{self.home_goals_for} – {self.home_goals_against}"

    @property
    def away_goals_for_against(self):
        return f"{self.away_goals_for} – {self.away_goals_against}"

    @property
    def average_goals_for(self):
        if self.matches_played == 0:
            return 0.0
        return self.goals_for / self.matches_played

    @property
    def average_goals_against(self):
        if self.matches_played == 0:
            return 0.0
        return self.goals_against / self.matches_played

    @property
    def average_home_goals_for(self):
        if self.home_matches_played == 0:
            return 0.0
        return self.home_goals_for / self.home_matches_played

    @property
    def average_home_goals_against(self):
        if self.home_matches_played == 0:
            return 0.0
        return self.home_goals_against / self.home_matches_played

    @property
    def average_away_goals_for(self):
        if self.away_matches_played == 0:
            return 0.0
        return self.away_goals_for / self.away_matches_played

    @property
    def average_away_goals_against(self):
        if self.away_matches_played == 0:
            return 0.0
        return self.away_goals_against / self.away_matches_played
