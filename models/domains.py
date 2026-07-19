from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Competition:
    id: int
    name: str
    country: str


@dataclass
class Season:
    id: int
    competition_id: int
    start_year: int
    end_year: int


@dataclass
class Team:
    id: int
    name: str


@dataclass
class Standing:
    team_id: int
    name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


@dataclass
class Bet:
    id: int
    date: str
    correct_count: int | None = None
    prize: int | None = None
    total_cost: int | None = None
    system: System = None
    coupon: Coupon = None


@dataclass
class BetDetails:
    bet_id: int
    match_number: int
    frame_value: str
    key_value: str | None = None
    mathematical: bool = False


@dataclass
class SoccerMatch:
    id: int
    season_id: int
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
class CouponMatch:
    number: int
    soccer_match: object


@dataclass
class Coupon:
    id: int
    year: int
    week: int
    soccer_matches: list["CouponMatch"] = field(default_factory=list)


@dataclass
class System:
    id: int
    system_type: str
    full_covers: int
    half_covers: int
    rows: int

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
            f"{self.rows}"
        )
