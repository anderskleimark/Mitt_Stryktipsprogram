from __future__ import annotations

from dataclasses import dataclass, field

from misc.country import Country


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
class Competition:
    id: int
    name: str
    country: str

    @property
    def flag_path(self):
        return Country.get_flag_path(self.country)

    @property
    def display_name(self):
        return self.name


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
class MatchAnalysis:

    home_statistics: TeamStatistics
    away_statistics: TeamStatistics

    lambda_home: float
    lambda_away: float

    probability_1: float
    probability_x: float
    probability_2: float

    probability_over_25: float
    probability_under_25: float

    probability_btts: float

    score_matrix: list[list[float]]


@dataclass
class Season:
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
        return f"{self.competition.name} {self.name}"


@dataclass
class SoccerMatch:
    id: int
    season_id: int
    competition: Competition
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


@dataclass
class Team:
    id: int
    name: str

    def __str__(self):
        return self.name


@dataclass
class TeamStatistics:

    team: Team

    matches_played: int = 0

    wins: int = 0
    draws: int = 0
    losses: int = 0

    goals_for: int = 0
    goals_against: int = 0

    home_matches: int = 0
    away_matches: int = 0

    home_goals_for: int = 0
    home_goals_against: int = 0

    away_goals_for: int = 0
    away_goals_against: int = 0

    average_goals_for: float = 0.0
    average_goals_against: float = 0.0

    average_home_goals_for: float = 0.0
    average_home_goals_against: float = 0.0

    average_away_goals_for: float = 0.0
    average_away_goals_against: float = 0.0

    attack_strength: float = 1.0
    defence_strength: float = 1.0

    recent_form: float = 0.0
