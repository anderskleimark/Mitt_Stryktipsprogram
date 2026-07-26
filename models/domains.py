from __future__ import annotations

from dataclasses import dataclass, field

from misc.country import Country


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


@dataclass
class Bet:
    """
        Representerar ett spelat stryktips- eller oddsspel.
    """
    id: int
    date: str
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
    mathematical: bool = False

# Representerar en fotbollstävling eller liga.


@dataclass
class Competition:
    """
        Representerar en fotbollstävling eller liga.
    """
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
    """
        Kopplar ett matchnummer på kupongen till en fotbollsmatch.
    """
    number: int
    soccer_match: SoccerMatch


@dataclass
class Coupon:
    """
        Representerar en stryktipskupong.
    """
    id: int
    year: int
    week: int
    soccer_matches: list["CouponMatch"] = field(default_factory=list)


@dataclass
class MatchAnalysis:
    """
        Innehåller resultatet av en analys av en fotbollsmatch.
    """

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
        return f"{self.competition.name} {self.name}"


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
    """
        Representerar ett fotbollslag.
    """
    id: int
    name: str

    def __str__(self):
        return self.name


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

    recent_form: float = 0.0

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
